import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { motion } from 'motion/react';
import { Lock, User, ArrowRight, AlertCircle, FileText, Eye, EyeOff } from 'lucide-react';
import Container from '../components/Container';
import Button from '../components/Button';
import { useAuth } from '../context/AuthContext';

export default function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const from = location.state?.from?.pathname || '/dashboard';

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await login(username.trim(), password);
      navigate(from, { replace: true });
    } catch (err) {
      let msg = 'Invalid username or password.';
      if (err.response?.status === 401) {
        msg = 'Invalid username or password.';
      } else if (err.response?.data) {
        const data = err.response.data;
        if (data.detail) {
          if (
            data.detail.toLowerCase().includes('no active account') ||
            data.detail.toLowerCase().includes('credential') ||
            data.detail.toLowerCase().includes('invalid')
          ) {
            msg = 'Invalid username or password.';
          } else {
            msg = data.detail;
          }
        } else if (data.non_field_errors) {
          msg = Array.isArray(data.non_field_errors) ? data.non_field_errors[0] : data.non_field_errors;
        }
      } else if (err.message) {
        msg = 'Unable to connect to the server. Please try again.';
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
              Sign In
            </h1>
            <p className="text-sm text-gray-500 mt-1">
              Sign in to your account, or create a new one to get started
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
                htmlFor="username"
                className="block text-xs font-semibold text-[#0a1b33] uppercase tracking-wider mb-1.5"
              >
                Username
              </label>
              <div className="relative rounded-2xl border border-gray-200 bg-white focus-within:border-[#0a152d] focus-within:ring-1 focus-within:ring-[#0a152d] transition-all">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-gray-400">
                  <User className="w-4 h-4" />
                </div>
                <input
                  id="username"
                  type="text"
                  required
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="Enter your username"
                  className="w-full pl-10 pr-4 py-3 text-sm text-[#0a1b33] bg-transparent rounded-2xl focus:outline-none"
                  disabled={loading}
                />
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label
                  htmlFor="password"
                  className="block text-xs font-semibold text-[#0a1b33] uppercase tracking-wider"
                >
                  Password
                </label>
                <Link
                  to="/forgot-password"
                  className="text-xs font-medium text-gray-500 hover:text-[#0a152d] transition-colors"
                >
                  Forgot password?
                </Link>
              </div>
              <div className="relative rounded-2xl border border-gray-200 bg-white focus-within:border-[#0a152d] focus-within:ring-1 focus-within:ring-[#0a152d] transition-all">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-gray-400">
                  <Lock className="w-4 h-4" />
                </div>
                <input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter your password"
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

            <div className="pt-2">
              <Button
                type="submit"
                variant="primary"
                size="lg"
                className="w-full justify-center"
                disabled={loading || !username.trim() || !password}
                icon={ArrowRight}
                iconPosition="right"
              >
                {loading ? 'Signing in...' : 'Sign In'}
              </Button>
            </div>
          </form>

          <div className="mt-8 pt-6 border-t border-gray-100 text-center text-xs text-gray-500">
            <span>Don't have an account yet? </span>
            <Link
              to="/register"
              className="font-semibold text-[#0a152d] hover:underline"
            >
              Create an account
            </Link>
          </div>
        </motion.div>
      </Container>
    </div>
  );
}

