import { motion } from 'framer-motion';
import { Loader2, Lock, Mail } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function LoginForm({
  form,
  errors,
  loading,
  submitError,
  onChange,
  onSubmit,
  className = '',
}) {
  return (
    <motion.div
      initial={{ opacity: 0, x: 24 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.55, ease: 'easeOut' }}
      className={`w-full rounded-[24px] border border-slate-200 bg-white p-6 shadow-[0_24px_56px_-28px_rgba(15,23,42,0.55)] sm:p-8 ${className}`}
    >
      <form onSubmit={onSubmit} className="space-y-4">
        {submitError && (
          <div className="rounded-xl border border-red-200 bg-red-50/90 px-4 py-3 text-sm text-red-700">
            {submitError}
          </div>
        )}

        <div>
          <label htmlFor="email" className="mb-1.5 block text-sm font-medium text-slate-700">
            Email
          </label>
          <div className="group relative">
            <Mail className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400 transition-colors group-focus-within:text-emerald-600" />
            <input
              id="email"
              name="email"
              type="email"
              value={form.email}
              onChange={onChange}
              placeholder="you@medicore.ai"
              className="block w-full rounded-2xl border border-slate-200 bg-white py-3 pl-11 pr-4 text-sm text-slate-900 shadow-sm outline-none transition-all focus:border-emerald-400 focus:ring-4 focus:ring-emerald-100"
              required
            />
          </div>
          {errors.email && <p className="mt-1.5 text-xs text-red-600">{errors.email}</p>}
        </div>

        <div>
          <label htmlFor="password" className="mb-1.5 block text-sm font-medium text-slate-700">
            Password
          </label>
          <div className="group relative">
            <Lock className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400 transition-colors group-focus-within:text-emerald-600" />
            <input
              id="password"
              name="password"
              type="password"
              value={form.password}
              onChange={onChange}
              placeholder="Enter your password"
              className="block w-full rounded-2xl border border-slate-200 bg-white py-3 pl-11 pr-4 text-sm text-slate-900 shadow-sm outline-none transition-all focus:border-emerald-400 focus:ring-4 focus:ring-emerald-100"
              required
            />
          </div>
          {errors.password && <p className="mt-1.5 text-xs text-red-600">{errors.password}</p>}
        </div>

        <label className="flex items-center gap-2.5 pt-1 text-sm text-slate-600">
          <input
            type="checkbox"
            name="rememberMe"
            checked={form.rememberMe}
            onChange={onChange}
            className="h-4 w-4 rounded border-slate-300 text-emerald-600 focus:ring-emerald-500"
          />
          Remember me on this device
        </label>

        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.985 }}
          type="submit"
          disabled={loading}
          className="inline-flex w-full items-center justify-center gap-2 rounded-2xl bg-emerald-600 px-5 py-3 text-sm font-semibold text-white shadow-lg shadow-emerald-600/30 transition-colors hover:bg-emerald-500 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
          {loading ? 'Signing in...' : 'Login to Dashboard'}
        </motion.button>
      </form>

      <p className="mt-6 text-sm text-slate-600">
        New to MediCore?{' '}
        <Link to="/signup" className="font-semibold text-emerald-700 transition-colors hover:text-emerald-600">
          Create account
        </Link>
      </p>
    </motion.div>
  );
}
