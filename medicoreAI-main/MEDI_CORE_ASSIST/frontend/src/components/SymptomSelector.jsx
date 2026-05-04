import { useState, useMemo } from 'react';
import { Search, Check, X } from 'lucide-react';
import clsx from 'clsx';

export default function SymptomSelector({ symptoms, selected, setSelected }) {
  const [filter, setFilter] = useState('');

  const filtered = useMemo(() => {
    if (!filter) return symptoms;
    const q = filter.toLowerCase();
    return symptoms.filter((s) => s.toLowerCase().includes(q));
  }, [filter, symptoms]);

  const toggle = (sym) =>
    setSelected((prev) =>
      prev.includes(sym) ? prev.filter((s) => s !== sym) : [...prev, sym],
    );

  return (
    <div className="card-padded space-y-5">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold text-slate-900">Select Symptoms</h2>
          <p className="text-sm text-slate-500">Choose the symptoms you are experiencing</p>
        </div>
        {selected.length > 0 && (
          <span className="badge-brand">
            {selected.length} selected
          </span>
        )}
      </div>

      {/* Search */}
      <div className="relative">
        <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
        <input
          type="text"
          placeholder="Search symptoms…"
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="input-field pl-10"
        />
      </div>

      {/* Grid */}
      <div className="max-h-[380px] overflow-y-auto rounded-xl border border-slate-200 p-2">
        {filtered.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-12 text-slate-400">
            <Search className="mb-2 h-8 w-8" />
            <p className="text-sm">No symptoms match your search</p>
          </div>
        ) : (
          <div className="grid gap-1.5 sm:grid-cols-2 lg:grid-cols-3">
            {filtered.map((sym) => {
              const active = selected.includes(sym);
              return (
                <button
                  key={sym}
                  type="button"
                  onClick={() => toggle(sym)}
                  className={clsx(
                    'flex items-center gap-2.5 rounded-lg px-3 py-2 text-left text-sm transition-colors',
                    active
                      ? 'bg-emerald-50 text-emerald-800 ring-1 ring-emerald-200'
                      : 'text-slate-700 hover:bg-slate-50',
                  )}
                >
                  <span
                    className={clsx(
                      'flex h-5 w-5 shrink-0 items-center justify-center rounded border transition-colors',
                      active
                        ? 'border-emerald-600 bg-emerald-600 text-white'
                        : 'border-slate-300 bg-white',
                    )}
                  >
                    {active && <Check className="h-3 w-3" />}
                  </span>
                  <span className="capitalize leading-tight">
                    {sym.replace(/_/g, ' ')}
                  </span>
                </button>
              );
            })}
          </div>
        )}
      </div>

      {/* Selected Tags */}
      {selected.length > 0 && (
        <div className="space-y-2 border-t border-slate-100 pt-4">
          <p className="text-xs font-medium text-slate-500 uppercase tracking-wider">
            Selected symptoms
          </p>
          <div className="flex flex-wrap gap-2">
            {selected.map((sym) => (
              <span
                key={sym}
                className="inline-flex items-center gap-1.5 rounded-full bg-emerald-50 px-3 py-1 text-xs font-medium text-emerald-700 ring-1 ring-emerald-200"
              >
                {sym.replace(/_/g, ' ')}
                <button
                  onClick={() => toggle(sym)}
                  className="rounded-full p-0.5 hover:bg-emerald-100"
                >
                  <X className="h-3 w-3" />
                </button>
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
