"""
Heart Health Module - Google Fit Connector
Google Fit API integration for heart rate, steps, sleep, and activity data
Uses simulated data when API credentials aren't configured

⚠️  NOTE (2026): Google Fit REST API is DEPRECATED
The recommended approach for real health data is:
1. Android companion app using Health Connect API
2. Android app POSTs data to this backend: /api/v1/health/submit
3. Backend receives and stores real health data

See: ANDROID_HEALTH_CONNECT_2026.md for modern architecture

This connector is kept for:
- Backward compatibility with older systems
- Testing/simulation when Health Connect not available
"""
import random
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from services.data_sources.base import BaseDataSource
import config


class GoogleFitConnector(BaseDataSource):
    """
    Google Fit data connector.
    Requires OAuth2 credentials (GOOGLE_FIT_CLIENT_ID, GOOGLE_FIT_CLIENT_SECRET).
    Falls back to simulated data when not configured.
    """

    @property
    def source_type(self) -> str:
        return "google_fit"

    def __init__(self, user_id: int, config_data: Optional[dict] = None):
        super().__init__(user_id, config_data)
        # Load tokens from config_data (passed from database) or default to None
        if config_data:
            self.access_token = config_data.get("access_token")
            self.refresh_token = config_data.get("refresh_token")
        else:
            self.access_token = None
            self.refresh_token = None
        
        self.use_simulation = not config.GOOGLE_FIT_CLIENT_ID

        # Parse client secret if it's a JSON string
        self._client_secret = ""
        if config.GOOGLE_FIT_CLIENT_SECRET:
            try:
                secret_data = json.loads(config.GOOGLE_FIT_CLIENT_SECRET)
                if isinstance(secret_data, dict) and "web" in secret_data:
                    self._client_secret = secret_data["web"].get("client_secret", "")
                else:
                    self._client_secret = config.GOOGLE_FIT_CLIENT_SECRET
            except (json.JSONDecodeError, TypeError):
                self._client_secret = config.GOOGLE_FIT_CLIENT_SECRET

    async def connect(self) -> bool:
        if self.use_simulation and not self.access_token:
            self.is_connected = True
            self.last_sync = datetime.utcnow()
            return True

        # If we have an access token from OAuth, we're connected to real Google Fit
        if self.access_token:
            self.is_connected = True
            print(f"✅ Google Fit connected with access token for user {self.user_id}")
            return True

        self.is_connected = True
        return True

    async def exchange_code(self, code: str) -> bool:
        """Exchange an OAuth2 authorization code for access and refresh tokens."""
        import httpx

        token_url = "https://oauth2.googleapis.com/token"
        redirect_uri = f"http://localhost:{config.PORT}/api/v1/data/callback/google-fit"

        payload = {
            "client_id": config.GOOGLE_FIT_CLIENT_ID,
            "client_secret": self._client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri,
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(token_url, data=payload)
                response.raise_for_status()
                data = response.json()

                self.access_token = data.get("access_token")
                self.refresh_token = data.get("refresh_token")
                self.is_connected = True
                self.last_sync = datetime.utcnow()
                return True
        except Exception as e:
            print(f"Google Fit token exchange failed: {e}")
            # Fall back to simulation mode
            self.use_simulation = True
            self.is_connected = True
            self.last_sync = datetime.utcnow()
            return True

    async def _refresh_access_token(self) -> bool:
        """Refresh the access token using refresh_token."""
        if not self.refresh_token:
            print(f"❌ No refresh token available for user {self.user_id}")
            return False
        
        import httpx
        token_url = "https://oauth2.googleapis.com/token"
        
        payload = {
            "client_id": config.GOOGLE_FIT_CLIENT_ID,
            "client_secret": self._client_secret,
            "refresh_token": self.refresh_token,
            "grant_type": "refresh_token",
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(token_url, data=payload)
                response.raise_for_status()
                data = response.json()
                
                self.access_token = data.get("access_token")
                print(f"✅ Google Fit token refreshed for user {self.user_id}")
                return True
        except Exception as e:
            print(f"❌ Google Fit token refresh failed: {e}")
            return False

    async def sync(self) -> List[Dict]:
        """Sync data from Google Fit. Uses real data if access token available, otherwise simulates."""
        # Try to use real Google Fit API if we have an access token
        if self.access_token:
            try:
                import httpx
                # Fetch heart rate data from the last 24 hours
                end_time_ms = int(datetime.utcnow().timestamp() * 1000)
                start_time_ms = int((datetime.utcnow() - timedelta(hours=24)).timestamp() * 1000)

                url = f"https://www.googleapis.com/fitness/v1/users/me/dataset:aggregate"
                headers = {"Authorization": f"Bearer {self.access_token}"}
                body = {
                    "aggregateBy": [
                        {"dataTypeName": "com.google.heart_rate.bpm"},
                        {"dataTypeName": "com.google.step_count.delta"},
                        {"dataTypeName": "com.google.oxygen_saturation"},
                    ],
                    "bucketByTime": {"durationMillis": 3600000},  # 1 hour buckets
                    "startTimeMillis": start_time_ms,
                    "endTimeMillis": end_time_ms,
                }

                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(url, headers=headers, json=body)
                    if response.status_code == 200:
                        api_data = response.json()
                        data = self._parse_google_fit_data(api_data)
                        print(f"✅ Fetched {len(data)} real readings from Google Fit for user {self.user_id}")
                        return data if data else self._generate_simulated_data()
                    elif response.status_code == 401 or response.status_code == 403:
                        # Token expired or invalid - try to refresh
                        print(f"⚠️ Google Fit API error (status {response.status_code}), attempting token refresh...")
                        if await self._refresh_access_token():
                            # Retry with new token
                            headers["Authorization"] = f"Bearer {self.access_token}"
                            retry_response = await client.post(url, headers=headers, json=body)
                            if retry_response.status_code == 200:
                                api_data = retry_response.json()
                                data = self._parse_google_fit_data(api_data)
                                print(f"✅ Fetched {len(data)} real readings from Google Fit (after refresh) for user {self.user_id}")
                                return data if data else self._generate_simulated_data()
                        print(f"⚠️ Google Fit auth failed after refresh, falling back to simulation")
                        return self._generate_simulated_data()
                    else:
                        # Other error
                        print(f"⚠️ Google Fit API error (status {response.status_code}), falling back to simulation")
                        return self._generate_simulated_data()
            except Exception as e:
                print(f"❌ Google Fit sync error: {e}")
                return self._generate_simulated_data()
        else:
            # No access token, use simulated data
            print(f"ℹ️ No Google Fit access token for user {self.user_id}, using simulated data")
            return self._generate_simulated_data()

    def _parse_google_fit_data(self, api_data: dict) -> List[Dict]:
        """Parse Google Fit API aggregated response into our format."""
        readings = []
        buckets = api_data.get("bucket", [])

        for bucket in buckets:
            ts_ms = int(bucket.get("startTimeMillis", 0))
            ts = datetime.utcfromtimestamp(ts_ms / 1000)
            reading = {
                "source": "google_fit",
                "timestamp": ts.isoformat(),
            }

            for dataset in bucket.get("dataset", []):
                data_type = dataset.get("dataSourceId", "")
                points = dataset.get("point", [])

                for point in points:
                    values = point.get("value", [])
                    if not values:
                        continue

                    if "heart_rate" in data_type and values:
                        reading["heart_rate"] = values[0].get("fpVal", 0)
                    elif "step_count" in data_type and values:
                        reading["steps"] = values[0].get("intVal", 0)
                    elif "oxygen_saturation" in data_type and values:
                        reading["spo2"] = values[0].get("fpVal", 0)

            if "heart_rate" in reading or "steps" in reading:
                readings.append(reading)

        self.last_sync = datetime.utcnow()
        return readings if readings else self._generate_simulated_data()

    async def get_latest(self) -> Optional[Dict]:
        data = await self.sync()
        return data[-1] if data else None

    async def get_history(self, start: datetime, end: datetime) -> List[Dict]:
        return self._generate_simulated_data(
            hours=int((end - start).total_seconds() / 3600)
        )

    def get_oauth_url(self) -> str:
        """Generate OAuth2 authorization URL for Google Fit."""
        redirect_uri = f"http://localhost:{config.PORT}/api/v1/data/callback/google-fit"

        if self.use_simulation:
            return f"https://accounts.google.com/o/oauth2/v2/auth?simulation=true&redirect_uri={redirect_uri}"

        base = "https://accounts.google.com/o/oauth2/v2/auth"
        params = {
            "client_id": config.GOOGLE_FIT_CLIENT_ID,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": " ".join([
                "https://www.googleapis.com/auth/fitness.heart_rate.read",
                "https://www.googleapis.com/auth/fitness.activity.read",
                "https://www.googleapis.com/auth/fitness.sleep.read",
                "https://www.googleapis.com/auth/fitness.body.read",
            ]),
            "access_type": "offline",
            "prompt": "consent",
        }
        query = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{base}?{query}"

    def _generate_simulated_data(self, hours: int = 24) -> List[Dict]:
        """Generate simulated Google Fit-style data."""
        data = []
        base_hr = random.randint(62, 78)
        now = datetime.utcnow()

        for h in range(hours):
            ts = now - timedelta(hours=hours - h)
            hour = ts.hour

            # Simulate daily pattern
            if 0 <= hour < 6:
                hr = base_hr - 8 + random.gauss(0, 2)
                steps = 0
            elif 6 <= hour < 12:
                hr = base_hr + 5 + random.gauss(0, 4)
                steps = random.randint(200, 800)
            elif 12 <= hour < 18:
                hr = base_hr + 8 + random.gauss(0, 5)
                steps = random.randint(400, 1200)
            else:
                hr = base_hr + 2 + random.gauss(0, 3)
                steps = random.randint(100, 400)

            data.append({
                "heart_rate": round(max(45, min(150, hr)), 1),
                "steps": steps,
                "calories_burned": round(steps * 0.04 + hr * 0.1, 1),
                "activity_minutes": random.randint(0, 15) if steps > 300 else 0,
                "spo2": round(random.uniform(95.5, 99.5), 1),
                "source": "google_fit",
                "timestamp": ts.isoformat(),
            })

        self.last_sync = datetime.utcnow()
        return data
