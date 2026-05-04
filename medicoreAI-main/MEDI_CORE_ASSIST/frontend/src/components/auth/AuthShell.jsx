import { Heart, ShieldCheck } from 'lucide-react';

export default function AuthShell({ title, subtitle, children, footer }) {
  return (
    <div className="relative min-h-screen overflow-hidden bg-gradient-to-br from-sky-50 via-white to-emerald-50 px-4 py-12">
      <div className="absolute -top-24 -left-20 h-72 w-72 rounded-full bg-sky-200/40 blur-3xl" />
      <div className="absolute -right-20 top-1/3 h-80 w-80 rounded-full bg-emerald-200/40 blur-3xl" />

      <div className="relative mx-auto grid w-full max-w-5xl gap-8 lg:grid-cols-2">
        <div className="rounded-3xl border border-white/60 bg-white/80 p-8 shadow-xl backdrop-blur">
          <div className="mb-6 flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-600 text-white">
              <Heart className="h-5 w-5" fill="currentColor" />
            </div>
            <div>
              <h1 className="text-lg font-bold text-slate-900">MediCore AI Assistant</h1>
              <p className="text-xs uppercase tracking-wide text-slate-400">Secure Patient Access</p>
            </div>
          </div>

          <h2 className="text-2xl font-bold text-slate-900">{title}</h2>
          <p className="mt-2 text-sm text-slate-500">{subtitle}</p>

          <div className="mt-6">{children}</div>

          {footer && <div className="mt-6 text-sm text-slate-600">{footer}</div>}
        </div>

        <div className="hidden items-center lg:flex">
          <div className="rounded-3xl border border-emerald-100 bg-white/75 p-8 shadow-lg backdrop-blur">
            <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-2xl bg-emerald-100 text-emerald-700">
              <ShieldCheck className="h-6 w-6" />
            </div>
            <h3 className="text-xl font-semibold text-slate-900">Your health data stays protected</h3>
            <ul className="mt-4 space-y-3 text-sm text-slate-600">
              <li>JWT session tokens with expiration and validation.</li>
              <li>Passwords are hashed with bcrypt before storage.</li>
              <li>Authenticated access to medical AI modules only.</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
