import clsx from 'clsx';

const RULES = [
  { id: 'length', label: 'At least 8 characters', test: (v) => v.length >= 8 },
  { id: 'upper', label: '1 uppercase letter', test: (v) => /[A-Z]/.test(v) },
  { id: 'lower', label: '1 lowercase letter', test: (v) => /[a-z]/.test(v) },
  { id: 'number', label: '1 number', test: (v) => /\d/.test(v) },
  { id: 'special', label: '1 special character', test: (v) => /[!@#$%^&*()_\-+={[}\]|\\:;"'<,>.?/`~]/.test(v) },
];

export function evaluatePassword(password) {
  const results = RULES.map((rule) => ({ ...rule, passed: rule.test(password) }));
  const score = results.filter((rule) => rule.passed).length;
  return { rules: results, score };
}

export default function PasswordStrengthHint({ password }) {
  const { rules, score } = evaluatePassword(password);
  const strengthLabel =
    score <= 2 ? 'Weak' : score === 3 || score === 4 ? 'Medium' : 'Strong';

  return (
    <div className="rounded-xl border border-slate-200 bg-slate-50 p-3">
      <div className="mb-2 flex items-center justify-between">
        <span className="text-xs font-medium text-slate-600">Password strength</span>
        <span
          className={clsx(
            'text-xs font-semibold',
            score <= 2 && 'text-red-600',
            (score === 3 || score === 4) && 'text-amber-600',
            score >= 5 && 'text-emerald-600',
          )}
        >
          {strengthLabel}
        </span>
      </div>
      <ul className="space-y-1">
        {rules.map((rule) => (
          <li
            key={rule.id}
            className={clsx(
              'text-xs',
              rule.passed ? 'text-emerald-700' : 'text-slate-500',
            )}
          >
            {rule.passed ? 'OK' : '•'} {rule.label}
          </li>
        ))}
      </ul>
    </div>
  );
}
