import { Activity, ClipboardList, FileText, Heart, Stethoscope } from 'lucide-react';
import { Link } from 'react-router-dom';
import ProfileForm from '../components/profile/ProfileForm';
import { useAuth } from '../context/AuthContext';

const MODULES = [
  {
    title: 'Disease Prediction',
    description: 'Predict possible conditions from selected symptoms.',
    to: '/dashboard/disease',
    icon: Activity,
  },
  {
    title: 'AI Consultation',
    description: 'Voice + image based guidance from the assistant.',
    to: '/dashboard/consultation',
    icon: Stethoscope,
  },
  {
    title: 'Prescription Analyzer',
    description: 'Extract medicines and view alternative options.',
    to: '/dashboard/prescription',
    icon: FileText,
  },
  {
    title: 'Health Report Analyzer',
    description: 'Interpret lab reports in plain language.',
    to: '/dashboard/health-analyzer',
    icon: ClipboardList,
  },
  {
    title: 'Heart Health Module',
    description: 'Cardiac monitoring, risk prediction & Cardia AI assistant.',
    to: '/dashboard/heart-health',
    icon: Heart,
  },
];

export default function DashboardHome() {
  const { user } = useAuth();

  return (
    <div className="space-y-6">
      <div className="card-padded">
        <h1 className="text-2xl font-bold text-slate-900">Welcome to MediCore Dashboard</h1>
        <p className="mt-2 text-sm text-slate-600">
          Signed in as <span className="font-semibold text-slate-800">{user?.email}</span>
        </p>
        <div className="mt-4 grid gap-3 sm:grid-cols-2">
          <div className="rounded-xl bg-slate-50 px-4 py-3">
            <p className="text-xs text-slate-500">Age</p>
            <p className="text-sm font-semibold text-slate-800">{user?.age ?? 'N/A'}</p>
          </div>
          <div className="rounded-xl bg-slate-50 px-4 py-3">
            <p className="text-xs text-slate-500">Blood Group</p>
            <p className="text-sm font-semibold text-slate-800">{user?.blood_group ?? 'N/A'}</p>
          </div>
        </div>
      </div>

      <ProfileForm />

      <div className="grid gap-4 sm:grid-cols-2">
        {MODULES.map(({ title, description, to, icon: Icon }) => (
          <Link key={to} to={to} className="card-padded group transition hover:border-emerald-200">
            <div className="mb-3 inline-flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-50 text-emerald-700 group-hover:bg-emerald-100">
              <Icon className="h-5 w-5" />
            </div>
            <h2 className="text-base font-semibold text-slate-900">{title}</h2>
            <p className="mt-1 text-sm text-slate-600">{description}</p>
          </Link>
        ))}
      </div>
    </div>
  );
}
