import clsx from 'clsx';
import { motion } from 'framer-motion';
import {
  AlertTriangle,
  BarChart3,
  BookOpen,
  CheckCircle2,
  ShieldAlert,
  Sparkles,
  Target,
} from 'lucide-react';

export default function PredictionResult({ data }) {
  const rankedPredictions = data.personalized_top_predictions || data.top_predictions || [];
  const primaryDisease = data.personalized_prediction || data.predicted_disease;
  const topAlternatives =
    rankedPredictions.length > 1
      ? rankedPredictions.slice(1, 4)
      : (data.top_predictions || []).slice(1, 4);

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35 }}
      className="space-y-5"
    >
      {(data.personalized_insights?.length > 0 || data.personalized_warnings?.length > 0) && (
        <div className="rounded-xl border border-emerald-200 bg-emerald-50 px-5 py-4">
          <div className="mb-2 flex items-center gap-2 text-sm font-semibold text-emerald-800">
            <Sparkles className="h-4 w-4" />
            {data.personalized_insight_label || 'Personalized Insight'}
          </div>

          {data.personalized_insights?.length > 0 && (
            <ul className="space-y-1.5">
              {data.personalized_insights.map((item, index) => (
                <li key={index} className="flex items-start gap-2 text-xs text-emerald-800">
                  <CheckCircle2 className="mt-0.5 h-3.5 w-3.5 shrink-0 text-emerald-600" />
                  {item}
                </li>
              ))}
            </ul>
          )}

          {data.personalized_warnings?.length > 0 && (
            <ul className="mt-2 space-y-1.5">
              {data.personalized_warnings.map((item, index) => (
                <li key={index} className="flex items-start gap-2 text-xs text-amber-800">
                  <AlertTriangle className="mt-0.5 h-3.5 w-3.5 shrink-0 text-amber-600" />
                  {item}
                </li>
              ))}
            </ul>
          )}
        </div>
      )}

      <div className="card overflow-hidden">
        <div className="bg-gradient-to-br from-emerald-600 to-teal-600 px-6 py-8 text-white">
          <div className="mb-2 flex items-center gap-2 text-sm font-medium text-emerald-200">
            <Target className="h-4 w-4" />
            Primary Prediction
          </div>
          <h3 className="text-2xl font-bold tracking-tight">{primaryDisease}</h3>
          {data.personalized_prediction && (
            <p className="mt-1 text-xs font-medium text-emerald-100">Based on your profile context</p>
          )}
        </div>

        {data.description && (
          <div className="border-b border-slate-100 px-6 py-5">
            <div className="mb-2 flex items-center gap-2">
              <BookOpen className="h-4 w-4 text-slate-400" />
              <h4 className="text-sm font-semibold text-slate-700">About this condition</h4>
            </div>
            <p className="text-sm leading-relaxed text-slate-600">{data.description}</p>
          </div>
        )}

        {data.precautions?.length > 0 && (
          <div className="px-6 py-5">
            <div className="mb-3 flex items-center gap-2">
              <ShieldAlert className="h-4 w-4 text-amber-500" />
              <h4 className="text-sm font-semibold text-slate-700">Recommended Precautions</h4>
            </div>
            <ul className="space-y-2">
              {data.precautions.map((precaution, index) => (
                <li key={index} className="flex items-start gap-2.5 text-sm text-slate-600">
                  <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-amber-400" />
                  {precaution}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {topAlternatives?.length > 0 && (
        <div className="card-padded">
          <div className="mb-4 flex items-center gap-2">
            <BarChart3 className="h-4 w-4 text-slate-400" />
            <h4 className="text-sm font-semibold text-slate-700">Alternative Possibilities</h4>
          </div>
          <div className="space-y-3">
            {topAlternatives.map((row, idx) => {
              const score = row.personalized_probability ?? row.probability ?? 0;
              return (
                <div key={row.disease} className="flex items-center gap-4">
                  <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-slate-100 text-xs font-bold text-slate-500">
                    {idx + 2}
                  </span>
                  <div className="min-w-0 flex-1">
                    <div className="mb-1 flex items-baseline justify-between">
                      <span className="truncate text-sm font-medium text-slate-800">{row.disease}</span>
                      <span className="ml-2 shrink-0 text-xs font-semibold text-slate-500">
                        {(score * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div className="h-1.5 w-full overflow-hidden rounded-full bg-slate-100">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${score * 100}%` }}
                        transition={{ duration: 0.6, delay: idx * 0.12 }}
                        className={clsx(
                          'h-full rounded-full',
                          idx === 0 ? 'bg-emerald-400' : idx === 1 ? 'bg-teal-400' : 'bg-slate-300',
                        )}
                      />
                    </div>
                    {row.description && <p className="mt-1 truncate text-xs text-slate-400">{row.description}</p>}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {data.personalized_recommendations?.length > 0 && (
        <div className="card-padded">
          <h4 className="mb-3 text-sm font-semibold text-slate-800">Based on your profile</h4>
          <ul className="space-y-2">
            {data.personalized_recommendations.map((item, index) => (
              <li key={index} className="text-sm text-slate-600">
                - {item}
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="card-padded">
        <h4 className="mb-3 text-xs font-semibold uppercase tracking-wider text-slate-400">
          Based on your symptoms
        </h4>
        <div className="flex flex-wrap gap-1.5">
          {data.input_symptoms.map((symptom) => (
            <span
              key={symptom}
              className="rounded-full bg-slate-100 px-2.5 py-0.5 text-xs font-medium capitalize text-slate-600"
            >
              {symptom.replace(/_/g, ' ')}
            </span>
          ))}
        </div>
      </div>

      <div className="rounded-xl border border-amber-200 bg-amber-50 px-5 py-4">
        <p className="text-xs leading-relaxed text-amber-800">
          <strong className="font-semibold">Important:</strong> This is an AI prediction for educational
          purposes only. Please consult qualified healthcare professionals for diagnosis and treatment.
        </p>
      </div>
    </motion.div>
  );
}
