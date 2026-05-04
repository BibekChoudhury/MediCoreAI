import { Heart } from 'lucide-react';
import { getApiBase } from '../api/client';

export default function HeartHealthModule() {
  const cacheBust = Date.now();
  const heartDashboardUrl = `${getApiBase()}/heart/static/dashboard/index.html?_=${cacheBust}`;

  return (
    <div className="space-y-4">
      <div className="card-padded">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-rose-50 text-rose-600">
            <Heart className="h-5 w-5" fill="currentColor" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-slate-900">Heart Health Module</h1>
            <p className="text-sm text-slate-500">
              AI-powered cardiac monitoring, risk prediction, ECG analysis &amp; Cardia assistant
            </p>
          </div>
        </div>
      </div>

      <div className="card overflow-hidden" style={{ height: 'calc(100vh - 220px)' }}>
        <iframe
          id="heart-health-iframe"
          src={heartDashboardUrl}
          title="Heart Health Command Center"
          className="h-full w-full border-0"
          allow="microphone; camera"
        />
      </div>
    </div>
  );
}
