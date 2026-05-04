import { useRef, useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import {
  AlertTriangle,
  CheckCircle2,
  ChevronDown,
  ChevronRight,
  FileImage,
  FileText,
  FlaskConical,
  Leaf,
  Loader2,
  Pill,
  Search,
  Syringe,
  Trash2,
  Upload,
} from 'lucide-react';
import clsx from 'clsx';
import { analyzePrescription } from '../api/client';

const ALLOWED_EXT = ['jpg', 'jpeg', 'png', 'pdf'];
const MAX_SIZE = 10 * 1024 * 1024;

export default function Prescription() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const inputRef = useRef(null);

  const handleFile = (event) => {
    const selectedFile = event.target.files[0];
    if (!selectedFile) {
      return;
    }

    const ext = selectedFile.name.split('.').pop().toLowerCase();
    if (!ALLOWED_EXT.includes(ext)) {
      setError('Unsupported format. Upload JPG, PNG, or PDF.');
      return;
    }
    if (selectedFile.size > MAX_SIZE) {
      setError('File exceeds 10 MB limit.');
      return;
    }

    setFile(selectedFile);
    setError(null);
    setResult(null);
    setPreview(selectedFile.type.startsWith('image/') ? URL.createObjectURL(selectedFile) : null);
  };

  const handleAnalyze = async () => {
    if (!file) {
      return;
    }
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await analyzePrescription(file);
      setResult(data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Analysis failed. Ensure the Prescription API is running.');
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setFile(null);
    setPreview(null);
    setResult(null);
    setError(null);
    if (inputRef.current) {
      inputRef.current.value = '';
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <div className="mb-1 flex items-center gap-2">
          <FileText className="h-5 w-5 text-emerald-600" />
          <h1 className="text-xl font-bold text-slate-900">Prescription Analyzer</h1>
        </div>
        <p className="text-sm text-slate-500">
          Upload a prescription to identify medicines and discover alternatives across Allopathy,
          Ayurveda and Homeopathy.
        </p>
      </div>

      {error && (
        <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      )}

      <div
        onClick={() => inputRef.current?.click()}
        className={clsx(
          'card flex cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed p-10 text-center transition-colors',
          file
            ? 'border-emerald-300 bg-emerald-50/30'
            : 'border-slate-200 bg-white hover:border-emerald-300 hover:bg-emerald-50/20',
        )}
      >
        {preview ? (
          <img src={preview} alt="Preview" className="max-h-52 rounded-xl object-contain shadow-sm" />
        ) : file ? (
          <div className="space-y-2">
            <FileImage className="mx-auto h-12 w-12 text-emerald-400" />
            <p className="text-sm font-semibold text-emerald-700">{file.name}</p>
          </div>
        ) : (
          <>
            <Upload className="mb-3 h-10 w-10 text-slate-300" />
            <p className="text-sm font-semibold text-slate-600">Click to upload prescription</p>
            <p className="mt-1 text-xs text-slate-400">JPG, PNG, or PDF - max 10 MB</p>
          </>
        )}
        <input
          ref={inputRef}
          type="file"
          accept=".jpg,.jpeg,.png,.pdf"
          onChange={handleFile}
          className="hidden"
        />
      </div>

      <div className="flex items-center gap-3">
        <button className="btn-primary" onClick={handleAnalyze} disabled={!file || loading}>
          {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4" />}
          {loading ? 'Analyzing...' : 'Analyze Prescription'}
        </button>
        <button className="btn-secondary" onClick={handleClear} disabled={loading}>
          <Trash2 className="h-4 w-4" />
          Clear
        </button>
      </div>

      {result && (
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="space-y-5">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-slate-900">Analysis Results</h2>
            <span className="badge-brand">
              {result.medicines.length} medicine{result.medicines.length !== 1 && 's'} found
            </span>
          </div>

          {(result.personalized_insights?.length > 0 || result.safety_warnings?.length > 0) && (
            <div className="rounded-xl border border-emerald-200 bg-emerald-50 px-5 py-4">
              <h3 className="mb-2 text-sm font-semibold text-emerald-800">
                {result.personalized_insight_label || 'Personalized Insight'}
              </h3>
              {result.personalized_insights?.length > 0 && (
                <ul className="space-y-1.5">
                  {result.personalized_insights.map((item, index) => (
                    <li key={index} className="flex items-start gap-2 text-xs text-emerald-800">
                      <CheckCircle2 className="mt-0.5 h-3.5 w-3.5 shrink-0 text-emerald-600" />
                      {item}
                    </li>
                  ))}
                </ul>
              )}
            </div>
          )}

          {Array.isArray(result.safety_warnings) && result.safety_warnings.length > 0 && (
            <div className="rounded-xl border border-amber-200 bg-amber-50 px-5 py-4">
              <p className="mb-2 text-sm font-semibold text-amber-800">Context-based safety warnings</p>
              <ul className="space-y-1.5">
                {result.safety_warnings.map((warning, index) => (
                  <li key={index} className="flex items-start gap-2 text-xs text-amber-700">
                    <AlertTriangle className="mt-0.5 h-3.5 w-3.5 shrink-0 text-amber-600" />
                    {warning}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {result.personalized_recommendations?.length > 0 && (
            <div className="card-padded">
              <h4 className="mb-2 text-sm font-semibold text-slate-800">Based on your profile</h4>
              <ul className="space-y-2">
                {result.personalized_recommendations.map((recommendation, index) => (
                  <li key={index} className="text-sm text-slate-600">
                    - {recommendation}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {result.medicines.map((med, idx) => (
            <MedicineCard key={idx} med={med} index={idx} />
          ))}

          <RawTextToggle text={result.raw_text} />

          <div className="rounded-xl border border-amber-200 bg-amber-50 px-5 py-4">
            <p className="text-xs leading-relaxed text-amber-800">
              <strong className="font-semibold">Disclaimer:</strong> {result.disclaimer}
            </p>
          </div>
        </motion.div>
      )}
    </div>
  );
}

function MedicineCard({ med, index }) {
  const categories = [
    { key: 'allopathy', label: 'Allopathy', icon: Syringe, color: 'blue', items: med.alternatives.allopathy },
    { key: 'ayurveda', label: 'Ayurveda', icon: Leaf, color: 'emerald', items: med.alternatives.ayurveda },
    { key: 'homeopathy', label: 'Homeopathy', icon: FlaskConical, color: 'purple', items: med.alternatives.homeopathy },
  ];

  const colorMap = {
    blue: {
      bg: 'bg-blue-50',
      ring: 'ring-blue-200',
      text: 'text-blue-700',
      icon: 'text-blue-500',
    },
    emerald: {
      bg: 'bg-emerald-50',
      ring: 'ring-emerald-200',
      text: 'text-emerald-700',
      icon: 'text-emerald-500',
    },
    purple: {
      bg: 'bg-purple-50',
      ring: 'ring-purple-200',
      text: 'text-purple-700',
      icon: 'text-purple-500',
    },
  };

  return (
    <div className="card overflow-hidden">
      <div className="flex items-center gap-4 border-b border-slate-100 px-5 py-4">
        <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-emerald-600 text-xs font-bold text-white">
          {index + 1}
        </span>
        <div className="min-w-0">
          <div className="flex flex-wrap items-baseline gap-2">
            <span className="text-base font-bold text-slate-900">{med.brand_name}</span>
            {med.generic_name && med.generic_name !== med.brand_name && (
              <span className="text-sm text-slate-400">({med.generic_name})</span>
            )}
          </div>
        </div>
        <Pill className="ml-auto h-5 w-5 shrink-0 text-slate-300" />
      </div>

      <div className="grid gap-4 p-5 sm:grid-cols-3">
        {categories.map(({ key, label, icon: Icon, color, items }) => {
          const c = colorMap[color];
          return (
            <div key={key} className={clsx('rounded-xl p-4 ring-1', c.bg, c.ring)}>
              <div className="mb-3 flex items-center gap-2">
                <Icon className={clsx('h-4 w-4', c.icon)} />
                <h5 className={clsx('text-xs font-semibold uppercase tracking-wider', c.text)}>{label}</h5>
              </div>
              {items.length > 0 ? (
                <ul className="space-y-2">
                  {items.map((alt, itemIndex) => (
                    <li key={itemIndex} className="text-sm text-slate-700">
                      <span className="font-medium">{alt.name}</span>
                      {alt.description && <span className="text-slate-500"> - {alt.description}</span>}
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-xs italic text-slate-400">No alternatives found</p>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

function RawTextToggle({ text }) {
  const [open, setOpen] = useState(false);
  if (!text) {
    return null;
  }

  return (
    <div className="card-padded">
      <button
        onClick={() => setOpen(!open)}
        className="flex items-center gap-2 text-sm font-medium text-slate-600 hover:text-slate-900"
      >
        {open ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
        {open ? 'Hide' : 'Show'} Raw OCR Text
      </button>
      <AnimatePresence>
        {open && (
          <motion.pre
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="mt-3 max-h-64 overflow-auto rounded-xl bg-slate-900 p-4 text-xs leading-relaxed text-slate-300 whitespace-pre-wrap"
          >
            {text}
          </motion.pre>
        )}
      </AnimatePresence>
    </div>
  );
}
