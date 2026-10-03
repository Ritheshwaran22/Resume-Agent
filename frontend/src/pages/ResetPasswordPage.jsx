import React, { useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { motion } from 'motion/react';
import { Lock, Eye, EyeOff, ArrowRight, AlertCircle, CheckCircle2, FileText, ArrowLeft, RefreshCw } from 'lucide-react';
import Container from '../components/Container';
import Button from '../components/Button';
import { confirmPasswordReset } from '../services/api';

export default function ResetPasswordPage() {
  const { uid, token } = useParams();
  const navigate = useNavigate();

  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const [isInvalidToken, setIsInvalidToken] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (newPassword !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }

    if (newPassword.length < 8) {
      setError('Password must be at least 8 characters long.');
      return;
    }

    setLoading(true);

    try {
      await confirmPasswordReset({
        uid,
        token,
        new_password: newPassword,
        confirm_password: confirmPassword,
      });
      setIsSuccess(true);
    } catch (err) {
      const data = err.response?.data;
      if (data?.detail) {
        if (Array.isArray(data.detail)) {
          setError(data.detail.join(' '));
        } else {
          setError(data.detail);
          if (data.detail.toLowerCase().includes('invalid') || data.detail.toLowerCase().includes('expired')) {
            setIsInvalidToken(true);
          }
        }
      } else if (data?.confirm_password) {
        setError(Array.isArray(data.confirm_password) ? data.confirm_password[0] : data.confirm_password);
      } else if (data?.new_password) {
        setError(Array.isArray(data.new_password) ? data.new_password[0] : data.new_password);
      } else {
        setError('Unable to reset password. The link may have expired or is invalid.');
        setIsInvalidToken(true);
      }
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
          {/* Header */}
          <div className="text-center mb-8">
            <div className="w-12 h-12 rounded-2xl bg-[#0a152d] text-white flex items-center justify-center mx-auto mb-4 shadow-xs">
              <FileText className="w-6 h-6" />
            </div>
            <h1 className="font-display font-bold text-2xl sm:text-3xl text-[#0a1b33]">
              Create a new password
            </h1>
            <p className="text-sm text-gray-500 mt-2 leading-relaxed">
              Choose a strong password to secure your account.
            </p>
          </div>

          {error && !isInvalidToken && !isSuccess && (
            <div className="mb-6 p-4 rounded-2xl bg-red-50 border border-red-100 flex items-start gap-2.5 text-xs text-red-700">
              <AlertCircle className="w-4 h-4 text-red-600 shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          {isSuccess ? (
            <div className="space-y-6">
              <div className="p-5 rounded-2xl bg-emerald-50/80 border border-emerald-100/90 text-left space-y-2">
                <div className="flex items-center gap-2 text-emerald-800 font-semibold text-sm">
                  <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0" />
                  <span>Password Reset Successfully</span>
                </div>
                <p className="text-xs text-emerald-700 leading-relaxed">
                  Your password has been reset successfully. You can now log in with your new password.
                </p>
              </div>

              <div className="pt-2">
                <Button
                  variant="primary"
                  size="lg"
                  className="w-full justify-center"
                  onClick={() => navigate('/login')}
                  icon={ArrowRight}
                  iconPosition="right"
                >
                  Go to Login
                </Button>
              </div>
            </div>
          ) : isInvalidToken ? (
            <div className="space-y-6 text-center">
              <div className="p-5 rounded-2xl bg-amber-50/80 border border-amber-100/90 text-left space-y-2">
                <div className="flex items-center gap-2 text-amber-900 font-semibold text-sm">
                  <AlertCircle className="w-5 h-5 text-amber-600 shrink-0" />
                  <span>Invalid or Expired Link</span>
                </div>
                <p className="text-xs text-amber-800 leading-relaxed">
                  This password reset link is invalid or has expired. Please request a new reset link.
                </p>
              </div>

              <div className="pt-2">
                <Button
                  variant="primary"
                  size="lg"
                  className="w-full justify-center"
                  onClick={() => navigate('/forgot-password')}
                  icon={RefreshCw}
                  iconPosition="right"
                >
                  Request new reset link
                </Button>
              </div>

              <div className="pt-2">
                <Link
                  to="/login"
                  className="text-xs font-medium text-gray-500 hover:text-[#0a152d] inline-flex items-center gap-1 transition-colors"
                >
                  <ArrowLeft className="w-3.5 h-3.5" /> Return to sign in
                </Link>
              </div>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label
                  htmlFor="new-password"
                  className="block text-xs font-semibold text-[#0a1b33] uppercase tracking-wider mb-1.5"
                >
                  New password (min 8 chars)
                </label>
                <div className="relative rounded-2xl border border-gray-200 bg-white focus-within:border-[#0a152d] focus-within:ring-1 focus-within:ring-[#0a152d] transition-all">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-gray-400">
                    <Lock className="w-4 h-4" />
                  </div>
                  <input
                    id="new-password"
                    type={showPassword ? 'text' : 'password'}
                    required
                    minLength={8}
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    placeholder="Enter your new password"
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
                  htmlFor="confirm-new-password"
                  className="block text-xs font-semibold text-[#0a1b33] uppercase tracking-wider mb-1.5"
                >
                  Confirm new password
                </label>
                <div className="relative rounded-2xl border border-gray-200 bg-white focus-within:border-[#0a152d] focus-within:ring-1 focus-within:ring-[#0a152d] transition-all">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-gray-400">
                    <Lock className="w-4 h-4" />
                  </div>
                  <input
                    id="confirm-new-password"
                    type={showConfirmPassword ? 'text' : 'password'}
                    required
                    minLength={8}
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="Re-enter your new password"
                    className="w-full pl-10 pr-11 py-3 text-sm text-[#0a1b33] bg-transparent rounded-2xl focus:outline-none"
                    disabled={loading}
                  />
                  <button
                    type="button"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    className="absolute inset-y-0 right-0 pr-3.5 flex items-center text-gray-400 hover:text-gray-600 focus:outline-none"
                    aria-label={showConfirmPassword ? 'Hide password' : 'Show password'}
                  >
                    {showConfirmPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>

              <div className="pt-2">
                <Button
                  type="submit"
                  variant="primary"
                  size="lg"
                  className="w-full justify-center"
                  disabled={loading || !newPassword || !confirmPassword}
                  icon={ArrowRight}
                  iconPosition="right"
                >
                  {loading ? 'Resetting password...' : 'Reset Password'}
                </Button>
              </div>

              <div className="pt-4 text-center">
                <Link
                  to="/login"
                  className="text-xs font-medium text-gray-500 hover:text-[#0a152d] inline-flex items-center gap-1 transition-colors"
                >
                  <ArrowLeft className="w-3.5 h-3.5" /> Return to sign in
                </Link>
              </div>
            </form>
          )}
        </motion.div>
      </Container>
    </div>
  );
}
