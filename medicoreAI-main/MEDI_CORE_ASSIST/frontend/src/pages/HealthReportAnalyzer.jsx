import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ClipboardList,
  Upload,
  Loader2,
  Trash2,
  FileImage,
  Search,
  AlertTriangle,
  AlertCircle,
  CheckCircle2,
  TrendingUp,
  TrendingDown,
  Minus,
  User,
  Calendar,
  FileText,
  Stethoscope,
  Printer,
  ChevronDown,
  ChevronRight,
  Sparkles,
} from 'lucide-react';
import clsx from 'clsx';
import { analyzeHealthReport } from '../api/client';

const ALLOWED_EXT = ['jpg', 'jpeg', 'png', 'pdf'];
const MAX_SIZE = 10 * 1024 * 1024;

const LOADING_MESSAGES = [
  'Reading your report…',
  'Identifying parameters…',
  'Generating insights…',
  'Almost there…',
];

export default function HealthReportAnalyzer() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [loadingMsgIdx, setLoadingMsgIdx] = useState(0);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [rawOpen, setRawOpen] = useState(false);
  const inputRef = useRef(null);
  const loadingIntervalRef = useRef(null);

  // Cycle through loading messages while analyzing
  useEffect(() => {
    if (loading) {
      setLoadingMsgIdx(0);
      loadingIntervalRef.current = setInterval(() => {
        setLoadingMsgIdx((i) => Math.min(i + 1, LOADING_MESSAGES.length - 1));
      }, 2200);
    } else {
      clearInterval(loadingIntervalRef.current);
    }
    return () => clearInterval(loadingIntervalRef.current);
  }, [loading]);

  const handleFile = (e) => {
    const f = e.target.files[0];
    if (!f) return;
    const ext = f.name.split('.').pop().toLowerCase();
    if (!ALLOWED_EXT.includes(ext)) {
      setError('Unsupported format. Upload JPG, PNG, or PDF.');
      return;
    }
    if (f.size > MAX_SIZE) {
      setError('File exceeds 10 MB limit.');
      return;
    }
    setFile(f);
    setError(null);
    setResult(null);
    setPreview(f.type.startsWith('image/') ? URL.createObjectURL(f) : null);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const f = e.dataTransfer.files[0];
    if (f) handleFile({ target: { files: [f] } });
  };

  const handleAnalyze = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await analyzeHealthReport(file);
      setResult(data);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          'Analysis failed. Please ensure the backend is running and the file is a readable lab report.'
      );
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setFile(null);
    setPreview(null);
    setResult(null);
    setError(null);
    setRawOpen(false);
    if (inputRef.current) inputRef.current.value = '';
  };

  const handlePrint = () => window.print();

  const analysis = result?.analysis;

  // Sort parameters: abnormal first, then normal
  const sortedParams = analysis?.parameters
    ? [...analysis.parameters].sort((a, b) => {
        const order = { high: 0, low: 1, normal: 2 };
        return (order[a.status] ?? 2) - (order[b.status] ?? 2);
      })
    : [];

  const hasCritical = analysis?.flags?.critical?.length > 0;
  const hasBorderline = analysis?.flags?.borderline?.length > 0;
  const profileWarnings = analysis?.profile_warnings || [];
  const profileRecommendations = analysis?.profile_recommendations || [];
  const profileInsights = analysis?.personalized_insights || [];

  return (
    <div className="space-y-6">
      {/* ── Header ── */}
      <div className="print:hidden">
        <div className="flex items-center gap-2 mb-1">
          <ClipboardList className="h-5 w-5 text-emerald-600" />
          <h1 className="text-xl font-bold text-slate-900">Health Report Analyzer</h1>
        </div>
        <p className="text-sm text-slate-500">
          Upload a blood test or lab report (PDF or image) to get a plain-English summary with
          flagged abnormal values — designed for patients, not doctors.
        </p>
      </div>

      {/* ── Error ── */}
      {error && (
        <div className="print:hidden rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700 flex items-start gap-2">
          <AlertCircle className="h-4 w-4 shrink-0 mt-0.5" />
          {error}
        </div>
      )}

      {/* ── Upload Box ── */}
      {!result && (
        <div
          onDrop={handleDrop}
          onDragOver={(e) => e.preventDefault()}
          onClick={() => !loading && inputRef.current?.click()}
          className={clsx(
            'print:hidden card flex cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed p-10 text-center transition-colors',
            file
              ? 'border-emerald-300 bg-emerald-50/30'
              : 'border-slate-200 bg-white hover:border-emerald-300 hover:bg-emerald-50/20',
            loading && 'pointer-events-none opacity-60'
          )}
        >
          {preview ? (
            <img src={preview} alt="Preview" className="max-h-52 rounded-xl object-contain shadow-sm" />
          ) : file ? (
            <div className="space-y-2">
              <FileImage className="mx-auto h-12 w-12 text-emerald-400" />
              <p className="text-sm font-semibold text-emerald-700">{file.name}</p>
              <p className="text-xs text-slate-400">PDF ready for analysis</p>
            </div>
          ) : (
            <>
              <Upload className="mb-3 h-10 w-10 text-slate-300" />
              <p className="text-sm font-semibold text-slate-600">
                Click or drag & drop your lab report
              </p>
              <p className="text-xs text-slate-400 mt-1">JPG, PNG, or PDF — max 10 MB</p>
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
      )}

      {/* ── Actions ── */}
      {!result && (
        <div className="print:hidden flex items-center gap-3">
          <button className="btn-primary" onClick={handleAnalyze} disabled={!file || loading}>
            {loading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Search className="h-4 w-4" />
            )}
            {loading ? LOADING_MESSAGES[loadingMsgIdx] : 'Analyze Report'}
          </button>
          <button className="btn-secondary" onClick={handleClear} disabled={loading}>
            <Trash2 className="h-4 w-4" />
            Clear
          </button>
        </div>
      )}

      {/* ── Loading Skeleton ── */}
      {loading && (
        <div className="print:hidden space-y-4">
          <SkeletonCard lines={2} />
          <SkeletonCard lines={4} />
          <SkeletonCard lines={3} />
        </div>
      )}

      {/* ── Results ── */}
      <AnimatePresence>
        {analysis && (
          <motion.div
            initial={{ opacity: 0, y: 14 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-5"
          >
            {/* Print header (hidden on screen) */}
            <div className="hidden print:block mb-6 pb-4 border-b border-slate-200">
              <h1 className="text-2xl font-bold text-slate-900">Health Report Summary</h1>
              <p className="text-xs text-slate-400 mt-1">Generated by MediCore AI — for patient reference only</p>
            </div>

            {/* ── Result Actions Bar ── */}
            <div className="print:hidden flex items-center justify-between flex-wrap gap-3">
              <h2 className="text-lg font-semibold text-slate-900">Your Report Summary</h2>
              <div className="flex gap-2">
                <button className="btn-secondary" onClick={handlePrint}>
                  <Printer className="h-4 w-4" />
                  Print / Save PDF
                </button>
                <button className="btn-secondary" onClick={handleClear}>
                  <Trash2 className="h-4 w-4" />
                  Clear
                </button>
              </div>
            </div>

            {/* A) Patient Info Bar */}
            <PatientInfoBar info={analysis.patient_info} />

            {/* B) Overall Summary Card */}
            <SummaryCard summary={analysis.summary} />

            {(profileInsights.length > 0 || profileWarnings.length > 0) && (
              <div className="rounded-xl border border-emerald-200 bg-emerald-50 px-5 py-4">
                <div className="mb-2 flex items-center gap-2 text-sm font-semibold text-emerald-800">
                  <Sparkles className="h-4 w-4" />
                  {analysis.personalized_insight_label || 'Personalized Insight'}
                </div>
                {profileInsights.length > 0 && (
                  <ul className="space-y-1.5">
                    {profileInsights.map((item, index) => (
                      <li key={index} className="text-xs text-emerald-800">
                        - {item}
                      </li>
                    ))}
                  </ul>
                )}
                {profileWarnings.length > 0 && (
                  <ul className="mt-2 space-y-1.5">
                    {profileWarnings.map((item, index) => (
                      <li key={index} className="text-xs text-amber-800">
                        - {item}
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            )}

            {/* D) Flags — shown before full table so critical items are visible first */}
            {(hasCritical || hasBorderline) && (
              <FlagsSection critical={analysis.flags.critical} borderline={analysis.flags.borderline} />
            )}

            {/* C) Parameters */}
            {sortedParams.length > 0 && (
              <ParametersSection params={sortedParams} />
            )}

            {/* E) Recommendations */}
            {analysis.recommendations?.length > 0 && (
              <RecommendationsSection items={analysis.recommendations} />
            )}

            {profileRecommendations.length > 0 && (
              <div className="card-padded">
                <p className="text-sm font-semibold text-slate-900 mb-2">Based on your profile</p>
                <ul className="space-y-2">
                  {profileRecommendations.map((item, index) => (
                    <li key={index} className="text-sm text-slate-600">
                      - {item}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Raw OCR toggle */}
            {result?.raw_text && (
              <div className="print:hidden card-padded">
                <button
                  onClick={() => setRawOpen(!rawOpen)}
                  className="flex items-center gap-2 text-sm font-medium text-slate-600 hover:text-slate-900"
                >
                  {rawOpen ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
                  {rawOpen ? 'Hide' : 'Show'} Raw Extracted Text
                </button>
                <AnimatePresence>
                  {rawOpen && (
                    <motion.pre
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: 'auto', opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      className="mt-3 max-h-64 overflow-auto rounded-xl bg-slate-900 p-4 text-xs leading-relaxed text-slate-300 whitespace-pre-wrap"
                    >
                      {result.raw_text}
                    </motion.pre>
                  )}
                </AnimatePresence>
              </div>
            )}

            {/* Disclaimer */}
            <div className="rounded-xl border border-amber-200 bg-amber-50 px-5 py-4">
              <p className="text-xs leading-relaxed text-amber-800">
                <strong className="font-semibold">Disclaimer:</strong> This summary is AI-generated
                for informational purposes only and is not a medical diagnosis. Always consult a
                qualified healthcare professional for medical advice and interpretation of test results.
              </p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

/* ─── Patient Info Bar ─── */
function PatientInfoBar({ info }) {
  if (!info) return null;
  const fields = [
    { icon: User, label: 'Patient', value: info.name || 'Not specified' },
    { icon: FileText, label: 'Report Type', value: info.report_type || 'Lab Report' },
    { icon: Calendar, label: 'Date', value: info.date || 'Not specified' },
    ...(info.age ? [{ icon: User, label: 'Age', value: info.age }] : []),
  ];
  return (
    <div className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3">
      <div className="flex flex-wrap gap-x-6 gap-y-2">
        {fields.map(({ icon: Icon, label, value }) => (
          <div key={label} className="flex items-center gap-1.5">
            <Icon className="h-3.5 w-3.5 text-slate-400" />
            <span className="text-xs text-slate-400">{label}:</span>
            <span className="text-xs font-semibold text-slate-700">{value}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

/* ─── Overall Summary Card ─── */
function SummaryCard({ summary }) {
  if (!summary) return null;
  return (
    <div className="card overflow-hidden">
      <div className="flex">
        <div className="w-1 shrink-0 bg-emerald-500 rounded-l-2xl" />
        <div className="flex-1 px-5 py-4">
          <p className="text-xs font-semibold uppercase tracking-wider text-emerald-600 mb-2">
            What your report says
          </p>
          <p className="text-sm leading-relaxed text-slate-700">{summary}</p>
        </div>
      </div>
    </div>
  );
}

/* ─── Flags Section ─── */
function FlagsSection({ critical, borderline }) {
  return (
    <div className="space-y-3">
      {critical?.length > 0 && (
        <div className="rounded-xl border border-red-200 bg-red-50 px-5 py-4">
          <div className="flex items-center gap-2 mb-2">
            <AlertTriangle className="h-4 w-4 text-red-600" />
            <p className="text-sm font-semibold text-red-800">Critical Values — See a Doctor Soon</p>
          </div>
          <ul className="space-y-1">
            {critical.map((item, i) => (
              <li key={i} className="text-sm text-red-700 flex items-center gap-2">
                <span className="h-1.5 w-1.5 rounded-full bg-red-500 shrink-0" />
                {item}
              </li>
            ))}
          </ul>
        </div>
      )}
      {borderline?.length > 0 && (
        <div className="rounded-xl border border-amber-200 bg-amber-50 px-5 py-4">
          <div className="flex items-center gap-2 mb-2">
            <AlertCircle className="h-4 w-4 text-amber-600" />
            <p className="text-sm font-semibold text-amber-800">Borderline Values — Worth Monitoring</p>
          </div>
          <ul className="space-y-1">
            {borderline.map((item, i) => (
              <li key={i} className="text-sm text-amber-700 flex items-center gap-2">
                <span className="h-1.5 w-1.5 rounded-full bg-amber-500 shrink-0" />
                {item}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

/* ─── Status Badge ─── */
function StatusBadge({ status }) {
  const cfg = {
    normal: {
      cls: 'bg-emerald-50 text-emerald-700 ring-1 ring-emerald-600/20',
      icon: CheckCircle2,
      label: 'Normal',
    },
    low: {
      cls: 'bg-blue-50 text-blue-700 ring-1 ring-blue-600/20',
      icon: TrendingDown,
      label: 'Low',
    },
    high: {
      cls: 'bg-red-50 text-red-700 ring-1 ring-red-600/20',
      icon: TrendingUp,
      label: 'High',
    },
  };
  const s = cfg[status?.toLowerCase()] ?? {
    cls: 'bg-slate-100 text-slate-600 ring-1 ring-slate-300',
    icon: Minus,
    label: status ?? '—',
  };
  const Icon = s.icon;
  return (
    <span
      className={clsx(
        'inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-semibold',
        s.cls
      )}
    >
      <Icon className="h-3 w-3" />
      {s.label}
    </span>
  );
}

/* ─── Parameters Section ─── */
function ParametersSection({ params }) {
  return (
    <div className="card overflow-hidden">
      <div className="border-b border-slate-100 px-5 py-3 flex items-center justify-between">
        <p className="text-sm font-semibold text-slate-900">Test Parameters</p>
        <p className="text-xs text-slate-400">
          {params.filter((p) => p.status !== 'normal').length} abnormal ·{' '}
          {params.filter((p) => p.status === 'normal').length} normal
        </p>
      </div>

      {/* Desktop table */}
      <div className="hidden sm:block overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-slate-50 text-left">
              <th className="px-5 py-3 text-xs font-semibold uppercase tracking-wider text-slate-500 w-1/4">
                Parameter
              </th>
              <th className="px-4 py-3 text-xs font-semibold uppercase tracking-wider text-slate-500">
                Your Value
              </th>
              <th className="px-4 py-3 text-xs font-semibold uppercase tracking-wider text-slate-500">
                Normal Range
              </th>
              <th className="px-4 py-3 text-xs font-semibold uppercase tracking-wider text-slate-500">
                Status
              </th>
              <th className="px-4 py-3 text-xs font-semibold uppercase tracking-wider text-slate-500">
                What it means
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {params.map((param, idx) => (
              <tr
                key={idx}
                className={clsx(
                  'transition-colors',
                  param.status === 'high' && 'bg-red-50/40',
                  param.status === 'low' && 'bg-blue-50/30'
                )}
              >
                <td className="px-5 py-3.5 font-semibold text-slate-900 whitespace-nowrap">
                  {param.name}
                </td>
                <td className="px-4 py-3.5 font-mono text-slate-800 whitespace-nowrap">
                  {param.value}
                  {param.unit && (
                    <span className="ml-1 text-xs text-slate-400">{param.unit}</span>
                  )}
                </td>
                <td className="px-4 py-3.5 text-xs text-slate-500 whitespace-nowrap">
                  {param.normal_range || '—'}
                </td>
                <td className="px-4 py-3.5">
                  <StatusBadge status={param.status} />
                </td>
                <td className="px-4 py-3.5 text-xs italic text-slate-500 max-w-xs">
                  {param.plain_english}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Mobile cards */}
      <div className="sm:hidden divide-y divide-slate-100">
        {params.map((param, idx) => (
          <div
            key={idx}
            className={clsx(
              'px-4 py-4',
              param.status === 'high' && 'bg-red-50/40',
              param.status === 'low' && 'bg-blue-50/30'
            )}
          >
            <div className="flex items-start justify-between gap-2 mb-1">
              <p className="text-sm font-semibold text-slate-900">{param.name}</p>
              <StatusBadge status={param.status} />
            </div>
            <p className="text-sm font-mono text-slate-800">
              {param.value}
              {param.unit && <span className="ml-1 text-xs text-slate-400">{param.unit}</span>}
              {param.normal_range && (
                <span className="ml-2 text-xs text-slate-400 font-sans">
                  (ref: {param.normal_range})
                </span>
              )}
            </p>
            {param.plain_english && (
              <p className="mt-1 text-xs italic text-slate-500">{param.plain_english}</p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

/* ─── Recommendations Section ─── */
function RecommendationsSection({ items }) {
  const tips = items.slice(0, -1);
  const doctorTip = items[items.length - 1];
  return (
    <div className="card-padded space-y-3">
      <p className="text-sm font-semibold text-slate-900">Recommendations</p>
      <ul className="space-y-2">
        {tips.map((tip, i) => (
          <li key={i} className="flex items-start gap-3">
            <CheckCircle2 className="h-4 w-4 shrink-0 mt-0.5 text-emerald-500" />
            <span className="text-sm text-slate-700">{tip}</span>
          </li>
        ))}
        {doctorTip && (
          <li className="flex items-start gap-3 mt-1 rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3">
            <Stethoscope className="h-4 w-4 shrink-0 mt-0.5 text-emerald-600" />
            <span className="text-sm font-medium text-emerald-800">{doctorTip}</span>
          </li>
        )}
      </ul>
    </div>
  );
}

/* ─── Skeleton Card ─── */
function SkeletonCard({ lines = 3 }) {
  return (
    <div className="card p-5 space-y-3 animate-pulse">
      <div className="h-3 w-1/3 rounded bg-slate-200" />
      {Array.from({ length: lines }).map((_, i) => (
        <div
          key={i}
          className="h-2.5 rounded bg-slate-100"
          style={{ width: `${70 + (i % 3) * 10}%` }}
        />
      ))}
    </div>
  );
}
