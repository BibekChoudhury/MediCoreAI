import { useState } from 'react';
import { motion } from 'framer-motion';
import LoginForm from '../components/login/LoginForm';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import landingGif from '../components/login/Landing.gif';

export default function Login() {
  const navigate = useNavigate();
  const { login } = useAuth();

  const [form, setForm] = useState({
    email: '',
    password: '',
    rememberMe: true,
  });
  const [errors, setErrors] = useState({});
  const [submitError, setSubmitError] = useState('');
  const [loading, setLoading] = useState(false);

  function handleChange(event) {
    const { name, value, type, checked } = event.target;
    setForm((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  }

  function validate() {
    const nextErrors = {};
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (!form.email.trim()) {
      nextErrors.email = 'Email is required.';
    } else if (!emailPattern.test(form.email.trim())) {
      nextErrors.email = 'Enter a valid email address.';
    }

    if (!form.password) {
      nextErrors.password = 'Password is required.';
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
      await login(form);
      navigate('/dashboard', { replace: true });
    } catch (error) {
      setSubmitError(error.response?.data?.detail || 'Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex h-screen w-full flex-col overflow-hidden lg:flex-row">
      <section className="flex h-[42vh] w-full items-center justify-center overflow-hidden bg-emerald-50 p-5 sm:p-8 lg:h-full lg:w-1/2 lg:p-10">
        <img
          src={landingGif}
          alt="MediCore healthcare landing visual"
          className="h-full w-full object-contain object-center"
        />
      </section>

      <section className="flex h-[58vh] w-full bg-gradient-to-br from-green-700 via-emerald-600 to-green-500 px-6 sm:px-10 lg:h-screen lg:w-1/2 lg:px-12">
        <div className="right-wrapper flex h-full w-full flex-col items-center justify-center">
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, ease: 'easeOut' }}
            className="content-container flex w-full max-w-[420px] flex-col gap-4"
          >
            <div className="text-left">
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-emerald-100">
                MediCore AI Assistant
              </p>
              <h1 className="mt-1.5 text-3xl font-bold leading-tight text-white sm:text-4xl">
                Welcome to MediCore AI
              </h1>
              <p className="mt-2 text-sm leading-relaxed text-emerald-50">
                Sign in to access your personalized healthcare dashboard.
              </p>
            </div>

            <LoginForm
              form={form}
              errors={errors}
              loading={loading}
              submitError={submitError}
              onChange={handleChange}
              onSubmit={handleSubmit}
            />
          </motion.div>
        </div>
      </section>
    </div>
  );
}
