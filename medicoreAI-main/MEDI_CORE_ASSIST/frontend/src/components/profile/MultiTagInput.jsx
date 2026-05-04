import { useState } from 'react';
import { Plus, X } from 'lucide-react';

export default function MultiTagInput({
  id,
  label,
  placeholder,
  values,
  onChange,
  helperText,
}) {
  const [draft, setDraft] = useState('');

  function addTag(rawValue) {
    const value = String(rawValue || '').trim();
    if (!value) {
      return;
    }

    const exists = values.some((item) => item.toLowerCase() === value.toLowerCase());
    if (!exists) {
      onChange([...values, value]);
    }
    setDraft('');
  }

  function removeTag(index) {
    onChange(values.filter((_, idx) => idx !== index));
  }

  function handleKeyDown(event) {
    if (event.key === 'Enter' || event.key === ',') {
      event.preventDefault();
      addTag(draft);
    }
    if (event.key === 'Backspace' && !draft && values.length > 0) {
      removeTag(values.length - 1);
    }
  }

  return (
    <div className="space-y-2">
      <label htmlFor={id} className="text-sm font-medium text-slate-700">
        {label}
      </label>
      <div className="rounded-xl border border-slate-300 bg-white p-3 focus-within:border-emerald-500 focus-within:ring-2 focus-within:ring-emerald-100">
        <div className="mb-2 flex flex-wrap gap-2">
          {values.map((tag, index) => (
            <span
              key={`${tag}-${index}`}
              className="inline-flex items-center gap-1 rounded-full bg-emerald-50 px-2.5 py-1 text-xs font-medium text-emerald-700"
            >
              {tag}
              <button
                type="button"
                onClick={() => removeTag(index)}
                className="rounded-full p-0.5 text-emerald-600 hover:bg-emerald-100"
              >
                <X className="h-3 w-3" />
              </button>
            </span>
          ))}
        </div>
        <div className="flex items-center gap-2">
          <input
            id={id}
            value={draft}
            onChange={(event) => setDraft(event.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            className="w-full border-0 p-0 text-sm text-slate-700 placeholder:text-slate-400 focus:outline-none focus:ring-0"
          />
          <button
            type="button"
            onClick={() => addTag(draft)}
            className="rounded-lg bg-slate-100 p-1.5 text-slate-500 hover:bg-slate-200"
            aria-label={`Add ${label}`}
          >
            <Plus className="h-4 w-4" />
          </button>
        </div>
      </div>
      {helperText ? <p className="text-xs text-slate-500">{helperText}</p> : null}
    </div>
  );
}
