"""
Heart Health Module - JARVIS Personality Engine
Generates friendly, casual, real-time conversational responses
Like talking to your best friend who genuinely cares about your health
"""
import random
from datetime import datetime
from typing import Optional


class JarvisPersonality:
    """
    Friend-mode personality engine — casual, warm, real-time.
    Talks like a caring buddy, not a clinical robot.
    """

    # ── Greeting Templates ────────────────────────────────

    GREETINGS = {
        "morning": [
            "Morning{name}! ☀️ Checked on you while you were sleeping — {status}",
            "Hey{name}! Rise and shine 🌅 Here's what's up with you: {status}",
            "Yo{name}! Good morning! Grabbed your health snapshot while you snoozed. {status}",
            "Mornin'{name}! ☕ Ready for the day? Let me catch you up — {status}",
        ],
        "afternoon": [
            "Hey{name}! How's your day going? Quick health check: {status}",
            "What's good{name}! 🙌 Took a peek at your numbers — {status}",
            "Hey there{name}! Afternoon check-in: {status}",
        ],
        "evening": [
            "Hey{name}! 🌙 Winding down? Here's how your heart did today: {status}",
            "Evening{name}! Let me give you the recap — {status}",
            "Hey{name}! Almost bedtime ✨ Quick health update: {status}",
        ],
        "generic": [
            "Hey{name}! 👋 Good to see you! {status}",
            "What's up{name}! I'm here whenever you need me. {status}",
            "Hey hey{name}! 😊 Let's talk heart health. {status}",
        ]
    }

    # ── Response Templates by Intent ──────────────────────

    PREDICTION_RESPONSES = {
        "Low": [
            "Ayy{name}! Great news 🎉 Your risk score is just {score}% — that's awesome! {factors} Whatever you're doing, keep it up! 💪",
            "Looking really good{name}! 🥳 You're sitting at {score}% risk which is super low. {factors} Your heart's in great shape!",
            "Niceee{name}! {score}% risk — your heart is vibing 💚 {factors} Keep crushing it!",
        ],
        "Moderate": [
            "Okay{name}, so here's the deal — your risk is at {score}%, which is in the middle zone. {factors} Nothing scary, but let's keep an eye on it together, yeah? 👀",
            "Hmm{name}, your score came back at {score}%. Not bad, not great. {factors} Think of it as a nudge to level up your health game a bit 🏃",
            "Got your results{name} — {score}% puts you in moderate territory. {factors} No need to stress but let's work on bringing that down 💪",
        ],
        "High": [
            "Hey{name}, I gotta be real with you — your risk score is {score}% and that's higher than I'd like to see. {factors} I really think you should chat with your doctor about this 🤝",
            "{name}, okay so this is important — {score}% is a high risk score. {factors} Please don't ignore this one, talk to your cardiologist soon ❤️",
            "Real talk{name} — your score of {score}% is in the high range. {factors} Let's get you to a doctor and figure out a plan together 🏥",
        ],
        "Critical": [
            "{name}, I need you to take this seriously — your risk is at {score}% which is really high. {factors} Please, please go see your doctor ASAP. I'm genuinely worried 🙏",
            "Hey{name}, no sugarcoating this one — {score}% is critical territory. {factors} Drop everything and call your healthcare provider right now. Your health comes first ❤️‍🔥",
        ]
    }

    ECG_RESPONSES = {
        "normal": [
            "Good news{name}! 🎵 Your ECG looks clean — nice steady rhythm, no drama. {details} Your heart's got a great beat!",
            "Your ECG is looking solid{name}! 💚 Everything's in rhythm. {details} Nothing to worry about here!",
            "All good on the ECG front{name}! 📊 Normal sinus rhythm — your heart's keeping the beat perfectly. {details}",
        ],
        "abnormal": [
            "Hey{name}, so I found some stuff in your ECG we should talk about. {details} Don't freak out, but definitely worth running by your doctor 👨‍⚕️",
            "Okay{name}, your ECG showed some interesting patterns. {details} Not saying it's bad, but let's get a professional to take a look, cool? 🩺",
            "Heads up{name} — I spotted some things in your ECG. {details} Could be nothing, but better safe than sorry! Let's get it checked ❤️",
        ]
    }

    ANGIOPLASTY_RESPONSES = [
        "Alright{name}, I went through your angioplasty report! 📋 Here's the TL;DR: {summary}\n\nAnd here's what that actually means for you: {explanation}",
        "Got it{name}! Read through everything. {summary}\n\nLet me break that down in normal-people language: {explanation} 😊",
    ]

    HEART_SOUND_RESPONSES = {
        "normal": [
            "Your heart sounds great{name}! 🎧 Nice clean lub-dub, no weird noises. {details} Music to my ears (literally lol)!",
            "All good{name}! 💓 Your heart's sounding healthy — clear S1, clear S2, no murmurs. {details}",
        ],
        "abnormal": [
            "Hey{name}, I picked up something in your heart recording we should chat about. {details} Not gonna lie, I'd feel better if a doc listened to this too 🩺",
            "Okay{name}, so I heard some unusual sounds in there. {details} Totally could be harmless, but let's play it safe and get it checked out ❤️",
        ]
    }

    MONITORING_RESPONSES = [
        "Here's your vibe check{name}! 💓 Heart rate: {hr} bpm ({status}), oxygen: {spo2}%, variability: {hrv}ms. {insight}",
        "Quick update{name}! Your heart's cruising at {hr} bpm, SpO2 at {spo2}%, HRV at {hrv}ms — overall looking {status}! {insight}",
        "Numbers check{name}! 📊 HR: {hr} bpm • O2: {spo2}% • HRV: {hrv}ms — {status}! {insight}",
    ]

    ALERT_RESPONSES = {
        "warning": [
            "Hey{name}, just a heads up 👀 — {detail} Wanna talk about it?",
            "Psst{name}, something caught my eye — {detail} Keep me posted on how you're feeling!",
            "Quick flag{name} ⚡ — {detail} Nothing to panic about, but let's keep watching.",
        ],
        "critical": [
            "Okay{name}, this is important and I'm not gonna play it cool — {detail} Please get this checked out today 🙏",
            "{name}, real talk here — {detail} This needs a doctor's attention ASAP. I've got your back ❤️",
        ],
        "emergency": [
            "{name}, stay with me — {detail} 🚨 I need you to call 108/911 right now. Can you tell me how you're feeling?",
            "This is serious{name} — {detail} Please sit down, call emergency services, and stay calm. I'm right here with you ❤️‍🔥",
        ]
    }

    ENCOURAGEMENT = [
        "Dude{name}, your numbers are actually getting better! 🔥 Keep doing what you're doing!",
        "No cap{name}, your consistency is paying off big time 📈 Proud of you!",
        "Look at you{name}! 🌟 Your health stats are trending up. You're killing it!",
        "Yesss{name}! 💪 Your hard work is showing in the numbers. Love to see it!",
    ]

    GENERAL_CHAT = [
        "Hey{name}! 😊 I'm here for whatever you need — check your vitals, break down a report, assess your risk... what's on your mind?",
        "What can I do for you{name}? I can peek at your health data, analyze reports, or just chat about your heart. You tell me! 💬",
        "I'm all ears{name}! 👂 Need a health check, report analysis, or just have a question? Fire away!",
    ]

    MEDICAL_DISCLAIMER = "\n\n💡 *Hey, quick reminder — I'm an AI buddy, not a doctor! Always double-check with your actual healthcare provider for big decisions. I've got your back, but they've got the stethoscope 🩺*"

    def __init__(self):
        self.style = "friendly"  # friendly, casual, brief

    def get_time_of_day(self) -> str:
        hour = datetime.now().hour
        if 5 <= hour < 12:
            return "morning"
        elif 12 <= hour < 17:
            return "afternoon"
        elif 17 <= hour < 22:
            return "evening"
        return "evening"

    def format_name(self, name: Optional[str] = None) -> str:
        if name:
            return f" {name}"
        return ""

    def greeting(self, name: Optional[str] = None, status: str = "Everything's looking solid! 💚") -> str:
        tod = self.get_time_of_day()
        templates = self.GREETINGS.get(tod, self.GREETINGS["generic"])
        template = random.choice(templates)
        return template.format(name=self.format_name(name), status=status)

    def prediction_response(self, name: str, risk_level: str, score: float,
                            factors_text: str = "") -> str:
        templates = self.PREDICTION_RESPONSES.get(risk_level, self.PREDICTION_RESPONSES["Moderate"])
        template = random.choice(templates)
        response = template.format(
            name=self.format_name(name),
            score=round(score * 100, 1),
            factors=factors_text
        )
        if risk_level in ("High", "Critical"):
            response += self.MEDICAL_DISCLAIMER
        return response

    def ecg_response(self, name: str, is_normal: bool, details: str = "") -> str:
        key = "normal" if is_normal else "abnormal"
        template = random.choice(self.ECG_RESPONSES[key])
        response = template.format(name=self.format_name(name), details=details)
        if not is_normal:
            response += self.MEDICAL_DISCLAIMER
        return response

    def angioplasty_response(self, name: str, summary: str, explanation: str) -> str:
        template = random.choice(self.ANGIOPLASTY_RESPONSES)
        response = template.format(
            name=self.format_name(name),
            summary=summary,
            explanation=explanation
        )
        response += self.MEDICAL_DISCLAIMER
        return response

    def heart_sound_response(self, name: str, is_normal: bool, details: str = "") -> str:
        key = "normal" if is_normal else "abnormal"
        template = random.choice(self.HEART_SOUND_RESPONSES[key])
        response = template.format(name=self.format_name(name), details=details)
        if not is_normal:
            response += self.MEDICAL_DISCLAIMER
        return response

    def monitoring_response(self, name: str, hr: float, spo2: float,
                           hrv: float, insight: str = "") -> str:
        if hr < 60:
            status = "a bit chill, huh"
        elif hr > 100:
            status = "running a bit hot 🔥"
        else:
            status = "smooth sailing 👌"

        template = random.choice(self.MONITORING_RESPONSES)
        return template.format(
            name=self.format_name(name),
            status=status,
            hr=round(hr),
            spo2=round(spo2, 1),
            hrv=round(hrv, 1),
            insight=insight
        )

    def alert_response(self, name: str, severity: str, detail: str) -> str:
        templates = self.ALERT_RESPONSES.get(severity, self.ALERT_RESPONSES["warning"])
        template = random.choice(templates)
        return template.format(name=self.format_name(name), detail=detail)

    def encouragement(self, name: Optional[str] = None) -> str:
        return random.choice(self.ENCOURAGEMENT).format(name=self.format_name(name))

    def general_response(self, name: Optional[str] = None) -> str:
        return random.choice(self.GENERAL_CHAT).format(name=self.format_name(name))

    def health_briefing(self, name: str, metrics: dict) -> str:
        """Generate a friendly health briefing."""
        hr = metrics.get("avg_heart_rate", "N/A")
        steps = metrics.get("total_steps", "N/A")
        sleep = metrics.get("sleep_quality", "unknown")
        hrv = metrics.get("avg_hrv", "N/A")
        anomalies = metrics.get("anomalies", [])

        briefing = self.greeting(name, "Let me catch you up on your health! 📊")
        briefing += f"\n\n💓 **Here's your snapshot:**\n"
        briefing += f"• Heart rate: **{hr} bpm** — "
        briefing += "nice and steady!\n" if isinstance(hr, (int, float)) and 60 <= hr <= 100 else "let's keep an eye on this\n"
        briefing += f"• HRV: **{hrv}ms**\n"
        briefing += f"• Steps: **{steps}** — "
        briefing += "crushing it! 🔥\n" if isinstance(steps, (int, float)) and steps > 8000 else "every step counts!\n"
        briefing += f"• Sleep: **{sleep}**\n"

        if anomalies:
            briefing += f"\n⚡ **Hey, heads up** — I spotted {len(anomalies)} thing(s) worth mentioning:\n"
            for a in anomalies[:3]:
                briefing += f"• {a}\n"
        else:
            briefing += "\n✅ No red flags at all — you're doing great! 💚"

        insights = metrics.get("insights", [])
        if insights:
            briefing += f"\n\n💡 **Pro tip:** {insights[0]}"

        return briefing


# Singleton instance
jarvis = JarvisPersonality()
