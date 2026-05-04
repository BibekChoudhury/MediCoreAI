import { NavLink, useLocation } from 'react-router-dom';
import {
  Activity,
  ClipboardList,
  FileText,
  Heart,
  LayoutDashboard,
  LogOut,
  Menu,
  Stethoscope,
  X,
} from 'lucide-react';
import { useState } from 'react';
import clsx from 'clsx';
import { useAuth } from '../context/AuthContext';

const NAV_ITEMS = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard, description: 'Account overview', exact: true },
  { to: '/dashboard/disease', label: 'Disease Prediction', icon: Activity, description: 'ML-powered diagnosis' },
  { to: '/dashboard/consultation', label: 'AI Consultation', icon: Stethoscope, description: 'Voice & image analysis' },
  { to: '/dashboard/prescription', label: 'Smart MedBuddy', icon: FileText, description: 'Medicine alternatives' },
  { to: '/dashboard/health-analyzer', label: 'Health Report Analyzer', icon: ClipboardList, description: 'Lab report insights' },
  { to: '/dashboard/heart-health', label: 'Heart Health', icon: Heart, description: 'Cardiac AI monitoring' },
];

export default function Layout({ children, meta, initError }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();
  const { user, logout } = useAuth();

  return (
    <div className="flex h-screen overflow-hidden bg-slate-50">
      {/* Mobile overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-30 bg-black/30 backdrop-blur-sm lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={clsx(
          'fixed inset-y-0 left-0 z-40 flex w-72 flex-col bg-white border-r border-slate-200 transition-transform duration-300 lg:static lg:translate-x-0',
          sidebarOpen ? 'translate-x-0' : '-translate-x-full',
        )}
      >
        {/* Brand */}
        <div className="flex h-16 items-center gap-3 border-b border-slate-100 px-6">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-emerald-600 shadow-sm">
            <Heart className="h-5 w-5 text-white" fill="currentColor" />
          </div>
          <div>
            <h1 className="text-base font-bold text-slate-900 tracking-tight">MediCore AI</h1>
            <p className="text-[10px] font-medium text-slate-400 uppercase tracking-widest">Medical Intelligence</p>
          </div>
          <button
            onClick={() => setSidebarOpen(false)}
            className="ml-auto rounded-lg p-1 text-slate-400 hover:bg-slate-100 lg:hidden"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 space-y-1 px-3 py-4">
          <p className="px-3 pb-2 text-[11px] font-semibold uppercase tracking-wider text-slate-400">
            Modules
          </p>
          {NAV_ITEMS.map(({ to, label, icon: Icon, description, exact }) => {
            const active = exact
              ? location.pathname === to
              : location.pathname === to || location.pathname.startsWith(`${to}/`);
            return (
              <NavLink
                key={to}
                to={to}
                onClick={() => setSidebarOpen(false)}
                className={clsx(
                  'group flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-colors',
                  active
                    ? 'bg-emerald-50 text-emerald-700'
                    : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900',
                )}
              >
                <span
                  className={clsx(
                    'flex h-8 w-8 items-center justify-center rounded-lg transition-colors',
                    active
                      ? 'bg-emerald-600 text-white shadow-sm'
                      : 'bg-slate-100 text-slate-500 group-hover:bg-slate-200',
                  )}
                >
                  <Icon className="h-4 w-4" />
                </span>
                <div className="min-w-0">
                  <p className="truncate">{label}</p>
                  <p
                    className={clsx(
                      'truncate text-[11px]',
                      active ? 'text-emerald-600/80' : 'text-slate-400',
                    )}
                  >
                    {description}
                  </p>
                </div>
              </NavLink>
            );
          })}
        </nav>

        {/* Model Stats Footer */}
        {meta && (
          <div className="border-t border-slate-100 px-4 py-4">
            <p className="mb-2 text-[11px] font-semibold uppercase tracking-wider text-slate-400">
              Model Info
            </p>
            <div className="grid grid-cols-2 gap-2">
              <Stat label="Model" value="Decision Tree" />
              <Stat label="Features" value={meta.n_features} />
              <Stat label="Diseases" value={meta.n_classes} />
              <Stat label="Status" value="Active" color="emerald" />
            </div>
          </div>
        )}
      </aside>

      {/* Main Content */}
      <div className="flex flex-1 flex-col overflow-hidden">
        {/* Top Bar */}
        <header className="flex h-16 shrink-0 items-center gap-4 border-b border-slate-200 bg-white px-4 sm:px-6">
          <button
            onClick={() => setSidebarOpen(true)}
            className="rounded-lg p-2 text-slate-500 hover:bg-slate-100 lg:hidden"
          >
            <Menu className="h-5 w-5" />
          </button>
          <div className="flex-1">
            <p className="text-sm font-semibold text-slate-800">{user?.email}</p>
            <p className="text-xs text-slate-500">
              Age: {user?.age} | Blood Group: {user?.blood_group} | Weight: {user?.weight ?? 'N/A'} kg | Gender: {user?.gender ?? 'N/A'}
            </p>
          </div>
          <div className="flex items-center gap-3">
            <div className="hidden items-center gap-2 text-xs text-slate-400 sm:flex">
              <span className="inline-block h-2 w-2 animate-pulse rounded-full bg-emerald-400" />
              Backend Connected
            </div>
            <button onClick={logout} className="btn-secondary py-2">
              <LogOut className="h-4 w-4" />
              Logout
            </button>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-y-auto">
          <div className="mx-auto max-w-5xl px-4 py-8 sm:px-6 lg:px-8">
            {initError && (
              <div className="mb-6 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                {initError}
              </div>
            )}
            {children}
          </div>
        </main>

        {/* Footer */}
        <footer className="border-t border-slate-200 bg-white px-6 py-3">
          <p className="text-center text-xs text-slate-400">
            This tool is for educational purposes only. Always consult healthcare professionals for medical advice.
          </p>
        </footer>
      </div>
    </div>
  );
}

function Stat({ label, value, color = 'slate' }) {
  const colors = {
    slate: 'text-slate-700',
    emerald: 'text-emerald-600',
  };
  return (
    <div className="rounded-lg bg-slate-50 px-2.5 py-1.5">
      <p className="text-[10px] font-medium text-slate-400">{label}</p>
      <p className={clsx('text-xs font-semibold', colors[color])}>{value}</p>
    </div>
  );
}
