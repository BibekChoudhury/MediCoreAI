import { useState, useMemo } from 'react';
import { Activity, Loader2, Trash2, Sparkles } from 'lucide-react';
import SymptomSelector from '../components/SymptomSelector';
import PredictionResult from '../components/PredictionResult';
import { predictDisease } from '../api/client';

export default function DiseasePrediction({ symptoms }) {
  const [selected, setSelected] = useState([]);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const canPredict = useMemo(() => selected.length > 0, [selected]);

  async function handlePredict() {
    if (!canPredict) return;
    setLoading(true);
    setError(null);
    try {
      const data = await predictDisease(selected);
      setResult(data);
    } catch (e) {
      setError(e.response?.data?.error || 'Prediction failed. Please try again.');
    } finally {
      setLoading(false);
    }
  }

  function handleClear() {
    setSelected([]);
    setResult(null);
    setError(null);
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <div className="flex items-center gap-2 mb-1">
          <Activity className="h-5 w-5 text-emerald-600" />
          <h1 className="text-xl font-bold text-slate-900">Disease Prediction</h1>
        </div>
        <p className="text-sm text-slate-500">
          Select your symptoms and our ML model will predict possible conditions.
        </p>
      </div>

      {/* Error */}
      {error && (
        <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      )}

      {/* Symptom Selector */}
      <SymptomSelector
        symptoms={symptoms}
        selected={selected}
        setSelected={setSelected}
      />

      {/* Actions */}
      <div className="flex items-center gap-3">
        <button
          className="btn-primary"
          disabled={!canPredict || loading}
          onClick={handlePredict}
        >
          {loading ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <Sparkles className="h-4 w-4" />
          )}
          {loading ? 'Analyzing…' : 'Predict Disease'}
        </button>
        <button
          className="btn-secondary"
          onClick={handleClear}
          disabled={loading}
        >
          <Trash2 className="h-4 w-4" />
          Clear All
        </button>
      </div>

      {/* Result */}
      {result && <PredictionResult data={result} />}
    </div>
  );
}
