import { useMemo, useState } from 'react';
import { Loader2 } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import AuthShell from '../components/auth/AuthShell';
import FormField from '../components/auth/FormField';
import PasswordStrengthHint, { evaluatePassword } from '../components/auth/PasswordStrengthHint';
import { useAuth } from '../context/AuthContext';

const BLOOD_GROUP_OPTIONS = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'];

export default function Signup() {
  const navigate = useNavigate();
  const { register } = useAuth();

  const [form, setForm] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    age: '',
    bloodGroup: '',
  });
  const [errors, setErrors] = useState({});
  const [submitError, setSubmitError] = useState('');
  const [loading, setLoading] = useState(false);

  const passwordEval = useMemo(() => evaluatePassword(form.password), [form.password]);

  function handleChange(event) {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  }

  function validate() {
    const nextErrors = {};
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (!form.email.trim()) {
      nextErrors.email = 'Email is required.';
    } else if (!emailPattern.test(form.email.trim())) {
      nextErrors.email = 'Enter a valid email address.';
    }

    if (!form.age) {
      nextErrors.age = 'Age is required.';
    } else {
      const ageNumber = Number(form.age);
      if (!Number.isInteger(ageNumber) || ageNumber < 1 || ageNumber > 120) {
        nextErrors.age = 'Age must be an integer between 1 and 120.';
      }
    }

    if (!form.bloodGroup) {
      nextErrors.bloodGroup = 'Please select your blood group.';
    }

    if (!form.password) {
      nextErrors.password = 'Password is required.';
    } else if (passwordEval.score < 5) {
      nextErrors.password = 'Password does not meet strength requirements.';
    }

    if (!form.confirmPassword) {
      nextErrors.confirmPassword = 'Please confirm your password.';
    } else if (form.password !== form.confirmPassword) {
      nextErrors.confirmPassword = 'Passwords do not match.';
    }

    setErrors(nextErrors);
    return Object.keys(nextErrors).length === 0;
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setSubmitError('');

    if (!validate()) {
      return;
    }

    setLoading(true);
    try {
      await register({
        email: form.email.trim(),
        password: form.password,
        age: Number(form.age),
        blood_group: form.bloodGroup,
      });
      navigate('/login', { replace: true });
    } catch (error) {
      setSubmitError(error.response?.data?.detail || 'Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <AuthShell
      title="Create your account"
      subtitle="Register once to unlock secure access to MediCore AI features."
      footer={(
        <p>
          Already have an account?{' '}
          <Link to="/login" className="font-semibold text-emerald-700 hover:text-emerald-600">
            Sign in
          </Link>
        </p>
      )}
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        {submitError && (
          <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            {submitError}
          </div>
        )}

        <FormField
          id="email"
          label="Email"
          type="email"
          name="email"
          value={form.email}
          onChange={handleChange}
          placeholder="you@example.com"
          error={errors.email}
          required
        />

        <div className="grid gap-4 sm:grid-cols-2">
          <FormField
            id="age"
            label="Age"
            type="number"
            name="age"
            value={form.age}
            onChange={handleChange}
            placeholder="e.g. 30"
            min={1}
            max={120}
            error={errors.age}
            required
          />

          <FormField
            id="bloodGroup"
            label="Blood Group"
            name="bloodGroup"
            value={form.bloodGroup}
            onChange={handleChange}
            error={errors.bloodGroup}
            required
          >
            <select
              id="bloodGroup"
              name="bloodGroup"
              value={form.bloodGroup}
              onChange={handleChange}
              className="input-field"
              required
            >
              <option value="">Select blood group</option>
              {BLOOD_GROUP_OPTIONS.map((group) => (
                <option key={group} value={group}>
                  {group}
                </option>
              ))}
            </select>
          </FormField>
        </div>

        <FormField
          id="password"
          label="Password"
          type="password"
          name="password"
          value={form.password}
          onChange={handleChange}
          placeholder="Create a strong password"
          error={errors.password}
          required
        />

        <PasswordStrengthHint password={form.password} />

        <FormField
          id="confirmPassword"
          label="Confirm Password"
          type="password"
          name="confirmPassword"
          value={form.confirmPassword}
          onChange={handleChange}
          placeholder="Re-enter your password"
          error={errors.confirmPassword}
          required
        />

        <button type="submit" className="btn-primary w-full" disabled={loading}>
          {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
          {loading ? 'Creating account...' : 'Create Account'}
        </button>
      </form>
    </AuthShell>
  );
}
