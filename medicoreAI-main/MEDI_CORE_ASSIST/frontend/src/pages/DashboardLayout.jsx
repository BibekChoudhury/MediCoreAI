import { useEffect, useState } from 'react';
import { Loader2 } from 'lucide-react';
import { Outlet } from 'react-router-dom';
import Layout from '../components/Layout';
import { fetchMetadata, fetchSymptoms } from '../api/client';

export default function DashboardLayout() {
  const [symptoms, setSymptoms] = useState([]);
  const [meta, setMeta] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [initError, setInitError] = useState('');

  useEffect(() => {
    async function loadData() {
      try {
        const [symptomList, metadata] = await Promise.all([
          fetchSymptoms(),
          fetchMetadata(),
        ]);
        setSymptoms(symptomList);
        setMeta(metadata);
      } catch (error) {
        setInitError(error.response?.data?.detail || 'Failed to load dashboard data from backend.');
      } finally {
        setIsLoading(false);
      }
    }

    loadData();
  }, []);

  return (
    <Layout meta={meta} initError={initError}>
      {isLoading ? (
        <div className="flex justify-center py-20">
          <div className="flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-600">
            <Loader2 className="h-4 w-4 animate-spin" />
            Loading dashboard...
          </div>
        </div>
      ) : (
        <Outlet context={{ symptoms }} />
      )}
    </Layout>
  );
}
