import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'motion/react';
import { Mail, ArrowRight, AlertCircle, CheckCircle2, FileText, ArrowLeft } from 'lucide-react';
import Container from '../components/Container';
import Button from '../components/Button';
import { requestPasswordReset } from '../services/api';

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email.trim()) return;

    setError('');
    setLoading(true);

    try {
      await requestPasswordReset(email.trim());
      setSubmitted(true);
    } catch (err) {
      if (err.response?.status === 429) {
        setError('Too many password reset requests. Please wait a while before trying again.');
      } else {
        // Return safe message without exposing backend traces
        setError('We could not process the password reset request right now. Please try again later.');
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
              Forgot your password?
            </h1>
            <p className="text-sm text-gray-500 mt-2 leading-relaxed">
              Enter the email address associated with your account.
            </p>
          </div>

          {error && (
            <div className="mb-6 p-4 rounded-2xl bg-red-50 border border-red-100 flex items-start gap-2.5 text-xs text-red-700">
              <AlertCircle className="w-4 h-4 text-red-600 shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          {submitted ? (
            <div className="space-y-6">
              <div className="p-5 rounded-2xl bg-emerald-50/80 border border-emerald-100/90 text-left space-y-2">
                <div className="flex items-center gap-2 text-emerald-800 font-semibold text-sm">
                  <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0" />
                  <span>Check your inbox</span>
                </div>
                <p className="text-xs text-emerald-700 leading-relaxed">
                  If an account exists with this email, you'll receive a password reset link shortly.
                </p>
              </div>

              <p className="text-xs text-gray-500 text-center">
                Didn't receive an email? Check your spam folder or ensure you entered your registered email address.
              </p>

              <div className="pt-2">
                <Link to="/login" className="block w-full">
                  <Button variant="outline" size="md" className="w-full justify-center" icon={ArrowLeft} iconPosition="left">
                    Back to Login
                  </Button>
                </Link>
              </div>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label
                  htmlFor="reset-email"
                  className="block text-xs font-semibold text-[#0a1b33] uppercase tracking-wider mb-1.5"
                >
                  Email
                </label>
                <div className="relative rounded-2xl border border-gray-200 bg-white focus-within:border-[#0a152d] focus-within:ring-1 focus-within:ring-[#0a152d] transition-all">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-gray-400">
                    <Mail className="w-4 h-4" />
                  </div>
                  <input
                    id="reset-email"
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="Enter your registered email"
                    className="w-full pl-10 pr-4 py-3 text-sm text-[#0a1b33] bg-transparent rounded-2xl focus:outline-none"
                    disabled={loading}
                  />
                </div>
              </div>

              <div className="pt-2">
                <Button
                  type="submit"
                  variant="primary"
                  size="lg"
                  className="w-full justify-center"
                  disabled={loading || !email.trim()}
                  icon={ArrowRight}
                  iconPosition="right"
                >
                  {loading ? 'Sending link...' : 'Send reset link'}
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
