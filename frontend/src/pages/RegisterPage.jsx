import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'motion/react';
import { Lock, User, Mail, ArrowRight, AlertCircle, FileText, Eye, EyeOff } from 'lucide-react';
import Container from '../components/Container';
import Button from '../components/Button';
import { useAuth } from '../context/AuthContext';

export default function RegisterPage() {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [password2, setPassword2] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showPassword2, setShowPassword2] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);


  const { register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (password !== password2) {
      setError('Passwords do not match.');
      return;
    }

    if (password.length < 8) {
      setError('Password must be at least 8 characters long.');
      return;
    }

    setLoading(true);

    try {
      await register(username.trim(), email.trim(), password, password2);
      navigate('/dashboard', { replace: true });
    } catch (err) {
      const data = err.response?.data;
      let msg = 'Registration failed. Please check your information.';
      if (data) {
        if (typeof data === 'string') {
          msg = data;
        } else if (data.username) {
          msg = Array.isArray(data.username) ? data.username[0] : data.username;
        } else if (data.email) {
          msg = Array.isArray(data.email) ? data.email[0] : data.email;
        } else if (data.password) {
          msg = Array.isArray(data.password) ? data.password[0] : data.password;
        } else if (data.non_field_errors) {
          msg = Array.isArray(data.non_field_errors) ? data.non_field_errors[0] : data.non_field_errors;
        } else if (data.detail) {
          msg = data.detail;
        }
      } else if (err.message) {
        msg = `Connection error (${err.message}). Please ensure the backend server is reachable.`;
      }
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="pt-28 pb-16 min-h-screen flex items-center justify-center">
      <Container size="compact">
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          className="bg-white rounded-3xl sm:rounded-[2.5rem] border border-gray-200/90 shadow-[0_4px_30px_-6px_rgba(10,27,51,0.04)] p-8 sm:p-12 max-w-md mx-auto"
        >
          {/* Top header */}
          <div className="text-center mb-8">
            <div className="w-12 h-12 rounded-2xl bg-[#0a152d] text-white flex items-center justify-center mx-auto mb-4 shadow-xs">
              <FileText className="w-6 h-6" />
            </div>
            <h1 className="font-display font-bold text-2xl sm:text-3xl text-[#0a1b33]">
              Create an account
            </h1>
            <p className="text-sm text-gray-500 mt-1">
              Start analyzing your resume with truthful AI feedback
            </p>
          </div>

          {error && (
            <div className="mb-6 p-4 rounded-2xl bg-red-50 border border-red-100 flex items-start gap-2.5 text-xs text-red-700">
              <AlertCircle className="w-4 h-4 text-red-600 shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label
                htmlFor="reg-username"
                className="block text-xs font-semibold text-[#0a1b33] uppercase tracking-wider mb-1.5"
              >
                Username
              </label>
              <div className="relative rounded-2xl border border-gray-200 bg-white focus-within:border-[#0a152d] focus-within:ring-1 focus-within:ring-[#0a152d] transition-all">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-gray-400">
                  <User className="w-4 h-4" />
                </div>
                <input
                  id="reg-username"
                  type="text"
                  required
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="Choose a username"
                  className="w-full pl-10 pr-4 py-3 text-sm text-[#0a1b33] bg-transparent rounded-2xl focus:outline-none"
                />
              </div>
            </div>

            <div>
              <label
                htmlFor="reg-email"
                className="block text-xs font-semibold text-[#0a1b33] uppercase tracking-wider mb-1.5"
              >
                Email Address
              </label>
              <div className="relative rounded-2xl border border-gray-200 bg-white focus-within:border-[#0a152d] focus-within:ring-1 focus-within:ring-[#0a152d] transition-all">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-gray-400">
                  <Mail className="w-4 h-4" />
                </div>
                <input
                  id="reg-email"
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="name@example.com"
                  className="w-full pl-10 pr-4 py-3 text-sm text-[#0a1b33] bg-transparent rounded-2xl focus:outline-none"
                />
              </div>
            </div>

            <div>
              <label
                htmlFor="reg-password"
                className="block text-xs font-semibold text-[#0a1b33] uppercase tracking-wider mb-1.5"
              >
                Password (min 8 chars)
              </label>
              <div className="relative rounded-2xl border border-gray-200 bg-white focus-within:border-[#0a152d] focus-within:ring-1 focus-within:ring-[#0a152d] transition-all">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-gray-400">
                  <Lock className="w-4 h-4" />
                </div>
                <input
                  id="reg-password"
                  type={showPassword ? 'text' : 'password'}
                  required
                  minLength={8}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Create a password"
                  className="w-full pl-10 pr-11 py-3 text-sm text-[#0a1b33] bg-transparent rounded-2xl focus:outline-none"
                  disabled={loading}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 pr-3.5 flex items-center text-gray-400 hover:text-gray-600 focus:outline-none"
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            <div>
              <label
                htmlFor="reg-confirm"
                className="block text-xs font-semibold text-[#0a1b33] uppercase tracking-wider mb-1.5"
              >
                Confirm Password
              </label>
              <div className="relative rounded-2xl border border-gray-200 bg-white focus-within:border-[#0a152d] focus-within:ring-1 focus-within:ring-[#0a152d] transition-all">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-gray-400">
                  <Lock className="w-4 h-4" />
                </div>
                <input
                  id="reg-confirm"
                  type={showPassword2 ? 'text' : 'password'}
                  required
                  minLength={8}
                  value={password2}
                  onChange={(e) => setPassword2(e.target.value)}
                  placeholder="Re-enter your password"
                  className="w-full pl-10 pr-11 py-3 text-sm text-[#0a1b33] bg-transparent rounded-2xl focus:outline-none"
                  disabled={loading}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword2(!showPassword2)}
                  className="absolute inset-y-0 right-0 pr-3.5 flex items-center text-gray-400 hover:text-gray-600 focus:outline-none"
                  aria-label={showPassword2 ? 'Hide password' : 'Show password'}
                >
                  {showPassword2 ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>


            <div className="pt-2">
              <Button
                type="submit"
                variant="primary"
                size="lg"
                className="w-full justify-center"
                disabled={loading || !username.trim() || !email.trim() || !password || !password2}
                icon={ArrowRight}
                iconPosition="right"
              >
                {loading ? 'Creating account...' : 'Create Account'}
              </Button>
            </div>
          </form>

          <div className="mt-8 pt-6 border-t border-gray-100 text-center text-xs text-gray-500">
            <span>Already have an account? </span>
            <Link
              to="/login"
              className="font-semibold text-[#0a152d] hover:underline"
            >
              Sign in
            </Link>
          </div>
        </motion.div>
      </Container>
    </div>
  );
}
