import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'motion/react';
import {
  User,
  Mail,
  Lock,
  ShieldAlert,
  CheckCircle2,
  AlertCircle,
  Trash2,
  Eye,
  EyeOff,
  FileText,
  BarChart3,
  Calendar,
  Loader2,
  X,
} from 'lucide-react';
import Container from '../components/Container';
import Button from '../components/Button';
import { useAuth } from '../context/AuthContext';
import {
  fetchCurrentUser,
  updateProfile,
  changePassword,
  deleteAccount,
} from '../services/api';

export default function SettingsPage() {
  const { user, updateUser, logout } = useAuth();
  const navigate = useNavigate();

  // Profile metadata state
  const [profile, setProfile] = useState(null);
  const [loadingProfile, setLoadingProfile] = useState(true);

  // Email update state
  const [email, setEmail] = useState('');
  const [emailLoading, setEmailLoading] = useState(false);
  const [emailSuccess, setEmailSuccess] = useState('');
  const [emailError, setEmailError] = useState('');

  // Password change state
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showCurrentPassword, setShowCurrentPassword] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [passwordLoading, setPasswordLoading] = useState(false);
  const [passwordSuccess, setPasswordSuccess] = useState('');
  const [passwordError, setPasswordError] = useState('');

  // Account deletion modal state
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [deleteConfirmationText, setDeleteConfirmationText] = useState('');
  const [deleteLoading, setDeleteLoading] = useState(false);
  const [deleteError, setDeleteError] = useState('');

  // Load latest account information on mount
  useEffect(() => {
    let isMounted = true;
    const loadProfile = async () => {
      try {
        const data = await fetchCurrentUser();
        if (isMounted) {
          setProfile(data);
          setEmail(data.email || '');
          updateUser(data);
        }
      } catch (err) {
        if (isMounted) {
          // Fall back to context user if available
          if (user) {
            setProfile(user);
            setEmail(user.email || '');
          }
        }
      } finally {
        if (isMounted) setLoadingProfile(false);
      }
    };
    loadProfile();
    return () => {
      isMounted = false;
    };
  }, []);

  // Handle email update
  const handleUpdateEmail = async (e) => {
    e.preventDefault();
    setEmailError('');
    setEmailSuccess('');

    const trimmedEmail = email.trim();
    if (!trimmedEmail) {
      setEmailError('Please enter a valid email address.');
      return;
    }

    if (trimmedEmail === profile?.email) {
      setEmailSuccess('Email address is already up to date.');
      return;
    }

    setEmailLoading(true);
    try {
      const updated = await updateProfile({ email: trimmedEmail });
      setProfile(updated);
      updateUser(updated);
      setEmailSuccess('Email address updated successfully.');
    } catch (err) {
      if (err.response?.data?.email) {
        const msg = Array.isArray(err.response.data.email)
          ? err.response.data.email[0]
          : err.response.data.email;
        setEmailError(msg);
      } else if (err.response?.data?.detail) {
        setEmailError(err.response.data.detail);
      } else {
        setEmailError('Could not update email address. Please try again.');
      }
    } finally {
      setEmailLoading(false);
    }
  };

  // Handle password change
  const handlePasswordChange = async (e) => {
    e.preventDefault();
    setPasswordError('');
    setPasswordSuccess('');

    if (!currentPassword) {
      setPasswordError('Please enter your current password.');
      return;
    }
    if (!newPassword) {
      setPasswordError('Please enter a new password.');
      return;
    }
    if (newPassword !== confirmPassword) {
      setPasswordError('New passwords do not match.');
      return;
    }

    setPasswordLoading(true);
    try {
      const res = await changePassword({
        current_password: currentPassword,
        new_password: newPassword,
        confirm_password: confirmPassword,
      });

      // Update fresh JWT tokens so session remains valid
      if (res.tokens?.access) {
        localStorage.setItem('access_token', res.tokens.access);
      }
      if (res.tokens?.refresh) {
        localStorage.setItem('refresh_token', res.tokens.refresh);
      }

      setPasswordSuccess('Password changed successfully.');
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
    } catch (err) {
      if (err.response?.data?.current_password) {
        const msg = Array.isArray(err.response.data.current_password)
          ? err.response.data.current_password[0]
          : err.response.data.current_password;
        setPasswordError(msg);
      } else if (err.response?.data?.confirm_password) {
        const msg = Array.isArray(err.response.data.confirm_password)
          ? err.response.data.confirm_password[0]
          : err.response.data.confirm_password;
        setPasswordError(msg);
      } else if (err.response?.data?.new_password) {
        const msg = Array.isArray(err.response.data.new_password)
          ? err.response.data.new_password.join(' ')
          : err.response.data.new_password;
        setPasswordError(msg);
      } else if (err.response?.data?.detail) {
        setPasswordError(err.response.data.detail);
      } else {
        setPasswordError('Failed to change password. Please verify your details.');
      }
    } finally {
      setPasswordLoading(false);
    }
  };

  // Handle permanent account deletion
  const handleDeleteAccount = async () => {
    if (deleteConfirmationText.trim().toUpperCase() !== 'DELETE MY ACCOUNT') {
      setDeleteError('Please type "DELETE MY ACCOUNT" exactly to confirm.');
      return;
    }

    setDeleteLoading(true);
    setDeleteError('');

    try {
      await deleteAccount();
      // Clear all local auth state
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');
      logout();
      navigate('/', {
        replace: true,
        state: { message: 'Your account and data have been permanently deleted.' },
      });
    } catch (err) {
      setDeleteError(
        err.response?.data?.detail ||
          'Failed to delete account. Please try again or contact support.'
      );
      setDeleteLoading(false);
    }
  };

  const formattedDate = profile?.date_joined
    ? new Date(profile.date_joined).toLocaleDateString(undefined, {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      })
    : 'Active member';

  return (
    <div className="pt-28 pb-20 min-h-screen bg-[#f9fafb]">
      <Container size="compact">
        {/* Page Header */}
        <div className="mb-8">
          <h1 className="font-display font-bold text-3xl sm:text-4xl text-[#0a1b33] tracking-tight">
            Account & Settings
          </h1>
          <p className="text-sm sm:text-base text-gray-500 mt-2">
            Manage your personal profile, credentials, and data privacy.
          </p>
        </div>

        <div className="space-y-6">
          {/* Card 1: Account Information */}
          <section className="bg-white rounded-3xl border border-gray-200/90 shadow-[0_4px_24px_-4px_rgba(10,27,51,0.04)] p-6 sm:p-8">
            <div className="flex items-center gap-3 mb-6 pb-4 border-b border-gray-100">
              <div className="w-10 h-10 rounded-2xl bg-[#0a152d] text-white flex items-center justify-center shadow-xs">
                <User className="w-5 h-5" />
              </div>
              <div>
                <h2 className="font-display font-semibold text-lg text-[#0a1b33]">
                  Account Overview
                </h2>
                <p className="text-xs text-gray-400">
                  Your registered profile and usage metrics
                </p>
              </div>
            </div>

            {loadingProfile ? (
              <div className="flex items-center justify-center py-8 text-gray-400">
                <Loader2 className="w-6 h-6 animate-spin mr-2" />
                <span className="text-sm">Loading account details...</span>
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                <div className="p-4 rounded-2xl bg-gray-50/80 border border-gray-100">
                  <div className="text-xs font-medium text-gray-400 mb-1 flex items-center gap-1.5">
                    <User className="w-3.5 h-3.5" />
                    <span>Username</span>
                  </div>
                  <div className="font-semibold text-sm text-[#0a1b33] truncate">
                    {profile?.username}
                  </div>
                  <span className="inline-block mt-2 px-2 py-0.5 rounded-md bg-gray-200/60 text-[10px] font-medium text-gray-600">
                    Read-only
                  </span>
                </div>

                <div className="p-4 rounded-2xl bg-gray-50/80 border border-gray-100">
                  <div className="text-xs font-medium text-gray-400 mb-1 flex items-center gap-1.5">
                    <Calendar className="w-3.5 h-3.5" />
                    <span>Member Since</span>
                  </div>
                  <div className="font-semibold text-sm text-[#0a1b33]">
                    {formattedDate}
                  </div>
                </div>

                <div className="p-4 rounded-2xl bg-gray-50/80 border border-gray-100">
                  <div className="text-xs font-medium text-gray-400 mb-1 flex items-center gap-1.5">
                    <FileText className="w-3.5 h-3.5" />
                    <span>Resumes Stored</span>
                  </div>
                  <div className="font-bold text-lg text-[#0a1b33]">
                    {profile?.total_resumes ?? 0}
                  </div>
                </div>

                <div className="p-4 rounded-2xl bg-gray-50/80 border border-gray-100 sm:col-span-2 lg:col-span-3">
                  <div className="text-xs font-medium text-gray-400 mb-1 flex items-center gap-1.5">
                    <BarChart3 className="w-3.5 h-3.5" />
                    <span>Total AI Analyses Completed</span>
                  </div>
                  <div className="font-bold text-lg text-[#0a1b33]">
                    {profile?.total_analyses ?? 0}
                  </div>
                </div>
              </div>
            )}
          </section>

          {/* Card 2: Update Email Address */}
          <section className="bg-white rounded-3xl border border-gray-200/90 shadow-[0_4px_24px_-4px_rgba(10,27,51,0.04)] p-6 sm:p-8">
            <div className="flex items-center gap-3 mb-6 pb-4 border-b border-gray-100">
              <div className="w-10 h-10 rounded-2xl bg-gray-100 text-[#0a152d] flex items-center justify-center">
                <Mail className="w-5 h-5" />
              </div>
              <div>
                <h2 className="font-display font-semibold text-lg text-[#0a1b33]">
                  Email Address
                </h2>
                <p className="text-xs text-gray-400">
                  Used for account communications and password recovery
                </p>
              </div>
            </div>

            {emailSuccess && (
              <div className="mb-5 p-3.5 rounded-2xl bg-emerald-50 border border-emerald-100 flex items-start gap-2.5 text-xs text-emerald-800">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                <span>{emailSuccess}</span>
              </div>
            )}

            {emailError && (
              <div className="mb-5 p-3.5 rounded-2xl bg-red-50 border border-red-100 flex items-start gap-2.5 text-xs text-red-700">
                <AlertCircle className="w-4 h-4 text-red-600 shrink-0 mt-0.5" />
                <span>{emailError}</span>
              </div>
            )}

            <form onSubmit={handleUpdateEmail} className="space-y-4 max-w-md">
              <div>
                <label
                  htmlFor="email-input"
                  className="block text-xs font-semibold text-gray-600 mb-1.5"
                >
                  Email Address
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-gray-400">
                    <Mail className="w-4 h-4" />
                  </div>
                  <input
                    id="email-input"
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full pl-10 pr-4 py-2.5 bg-gray-50 border border-gray-200 rounded-2xl text-sm text-[#0a1b33] placeholder-gray-400 focus:bg-white focus:outline-none focus:ring-2 focus:ring-[#0a152d]/15 focus:border-[#0a152d] transition-all"
                    placeholder="name@example.com"
                  />
                </div>
              </div>

              <div>
                <Button
                  type="submit"
                  size="md"
                  disabled={emailLoading}
                  className="w-full sm:w-auto"
                >
                  {emailLoading ? (
                    <span className="flex items-center gap-2">
                      <Loader2 className="w-4 h-4 animate-spin" />
                      Saving changes...
                    </span>
                  ) : (
                    'Update Email'
                  )}
                </Button>
              </div>
            </form>
          </section>

          {/* Card 3: Change Password */}
          <section className="bg-white rounded-3xl border border-gray-200/90 shadow-[0_4px_24px_-4px_rgba(10,27,51,0.04)] p-6 sm:p-8">
            <div className="flex items-center gap-3 mb-6 pb-4 border-b border-gray-100">
              <div className="w-10 h-10 rounded-2xl bg-gray-100 text-[#0a152d] flex items-center justify-center">
                <Lock className="w-5 h-5" />
              </div>
              <div>
                <h2 className="font-display font-semibold text-lg text-[#0a1b33]">
                  Change Password
                </h2>
                <p className="text-xs text-gray-400">
                  Ensure your account uses a secure, strong password
                </p>
              </div>
            </div>

            {passwordSuccess && (
              <div className="mb-5 p-3.5 rounded-2xl bg-emerald-50 border border-emerald-100 flex items-start gap-2.5 text-xs text-emerald-800">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                <span>{passwordSuccess}</span>
              </div>
            )}

            {passwordError && (
              <div className="mb-5 p-3.5 rounded-2xl bg-red-50 border border-red-100 flex items-start gap-2.5 text-xs text-red-700">
                <AlertCircle className="w-4 h-4 text-red-600 shrink-0 mt-0.5" />
                <span>{passwordError}</span>
              </div>
            )}

            <form onSubmit={handlePasswordChange} className="space-y-4 max-w-md">
              {/* Current Password */}
              <div>
                <label
                  htmlFor="current-password"
                  className="block text-xs font-semibold text-gray-600 mb-1.5"
                >
                  Current Password
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-gray-400">
                    <Lock className="w-4 h-4" />
                  </div>
                  <input
                    id="current-password"
                    type={showCurrentPassword ? 'text' : 'password'}
                    required
                    value={currentPassword}
                    onChange={(e) => setCurrentPassword(e.target.value)}
                    className="w-full pl-10 pr-10 py-2.5 bg-gray-50 border border-gray-200 rounded-2xl text-sm text-[#0a1b33] placeholder-gray-400 focus:bg-white focus:outline-none focus:ring-2 focus:ring-[#0a152d]/15 focus:border-[#0a152d] transition-all"
                    placeholder="Enter current password"
                  />
                  <button
                    type="button"
                    onClick={() => setShowCurrentPassword(!showCurrentPassword)}
                    className="absolute inset-y-0 right-0 pr-3.5 flex items-center text-gray-400 hover:text-gray-600"
                    aria-label="Toggle password visibility"
                  >
                    {showCurrentPassword ? (
                      <EyeOff className="w-4 h-4" />
                    ) : (
                      <Eye className="w-4 h-4" />
                    )}
                  </button>
                </div>
              </div>

              {/* New Password */}
              <div>
                <label
                  htmlFor="new-password"
                  className="block text-xs font-semibold text-gray-600 mb-1.5"
                >
                  New Password
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-gray-400">
                    <Lock className="w-4 h-4" />
                  </div>
                  <input
                    id="new-password"
                    type={showNewPassword ? 'text' : 'password'}
                    required
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    className="w-full pl-10 pr-10 py-2.5 bg-gray-50 border border-gray-200 rounded-2xl text-sm text-[#0a1b33] placeholder-gray-400 focus:bg-white focus:outline-none focus:ring-2 focus:ring-[#0a152d]/15 focus:border-[#0a152d] transition-all"
                    placeholder="Enter new password"
                  />
                  <button
                    type="button"
                    onClick={() => setShowNewPassword(!showNewPassword)}
                    className="absolute inset-y-0 right-0 pr-3.5 flex items-center text-gray-400 hover:text-gray-600"
                    aria-label="Toggle password visibility"
                  >
                    {showNewPassword ? (
                      <EyeOff className="w-4 h-4" />
                    ) : (
                      <Eye className="w-4 h-4" />
                    )}
                  </button>
                </div>
              </div>

              {/* Confirm New Password */}
              <div>
                <label
                  htmlFor="confirm-password"
                  className="block text-xs font-semibold text-gray-600 mb-1.5"
                >
                  Confirm New Password
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-gray-400">
                    <Lock className="w-4 h-4" />
                  </div>
                  <input
                    id="confirm-password"
                    type={showConfirmPassword ? 'text' : 'password'}
                    required
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    className="w-full pl-10 pr-10 py-2.5 bg-gray-50 border border-gray-200 rounded-2xl text-sm text-[#0a1b33] placeholder-gray-400 focus:bg-white focus:outline-none focus:ring-2 focus:ring-[#0a152d]/15 focus:border-[#0a152d] transition-all"
                    placeholder="Repeat new password"
                  />
                  <button
                    type="button"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    className="absolute inset-y-0 right-0 pr-3.5 flex items-center text-gray-400 hover:text-gray-600"
                    aria-label="Toggle password visibility"
                  >
                    {showConfirmPassword ? (
                      <EyeOff className="w-4 h-4" />
                    ) : (
                      <Eye className="w-4 h-4" />
                    )}
                  </button>
                </div>
              </div>

              <div>
                <Button
                  type="submit"
                  size="md"
                  disabled={passwordLoading}
                  className="w-full sm:w-auto"
                >
                  {passwordLoading ? (
                    <span className="flex items-center gap-2">
                      <Loader2 className="w-4 h-4 animate-spin" />
                      Updating Password...
                    </span>
                  ) : (
                    'Change Password'
                  )}
                </Button>
              </div>
            </form>
          </section>

          {/* Card 4: Danger Zone (Account Deletion) */}
          <section className="bg-white rounded-3xl border border-red-200 shadow-[0_4px_24px_-4px_rgba(239,68,68,0.06)] p-6 sm:p-8">
            <div className="flex items-center gap-3 mb-6 pb-4 border-b border-red-100">
              <div className="w-10 h-10 rounded-2xl bg-red-50 text-red-600 flex items-center justify-center">
                <ShieldAlert className="w-5 h-5" />
              </div>
              <div>
                <h2 className="font-display font-semibold text-lg text-red-700">
                  Danger Zone
                </h2>
                <p className="text-xs text-red-500/80">
                  Irreversible actions concerning your account and personal data
                </p>
              </div>
            </div>

            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-5 rounded-2xl bg-red-50/40 border border-red-100">
              <div>
                <div className="font-semibold text-sm text-[#0a1b33]">
                  Delete Account & All Data
                </div>
                <p className="text-xs text-gray-500 mt-1 max-w-lg leading-relaxed">
                  Permanently deletes your account, all uploaded resume files, job
                  descriptions, and analysis records. This operation cannot be undone.
                </p>
              </div>
              <button
                type="button"
                onClick={() => {
                  setDeleteConfirmationText('');
                  setDeleteError('');
                  setDeleteModalOpen(true);
                }}
                className="shrink-0 px-4 py-2.5 rounded-full text-xs font-semibold bg-red-600 hover:bg-red-700 text-white transition-colors cursor-pointer shadow-xs flex items-center justify-center gap-2"
              >
                <Trash2 className="w-4 h-4" />
                <span>Delete Account</span>
              </button>
            </div>
          </section>
        </div>
      </Container>

      {/* Confirmation Modal */}
      <AnimatePresence>
        {deleteModalOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-xs">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              transition={{ duration: 0.2 }}
              className="bg-white rounded-3xl border border-gray-200 max-w-md w-full p-6 sm:p-8 shadow-2xl relative"
            >
              <button
                type="button"
                onClick={() => setDeleteModalOpen(false)}
                className="absolute top-5 right-5 p-1.5 rounded-full text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-colors"
                aria-label="Close dialog"
              >
                <X className="w-5 h-5" />
              </button>

              <div className="w-12 h-12 rounded-2xl bg-red-100 text-red-600 flex items-center justify-center mb-4">
                <Trash2 className="w-6 h-6" />
              </div>

              <h3 className="font-display font-bold text-xl text-[#0a1b33]">
                Delete your account?
              </h3>
              <p className="text-xs sm:text-sm text-gray-500 mt-2 leading-relaxed">
                This action is <strong className="text-red-600 font-semibold">permanent</strong>.
                All your stored resume files, job descriptions, analysis histories, and account
                credentials will be purged immediately.
              </p>

              {deleteError && (
                <div className="mt-4 p-3 rounded-xl bg-red-50 border border-red-100 text-xs text-red-700 flex items-start gap-2">
                  <AlertCircle className="w-4 h-4 text-red-600 shrink-0 mt-0.5" />
                  <span>{deleteError}</span>
                </div>
              )}

              <div className="mt-5">
                <label
                  htmlFor="delete-confirm-input"
                  className="block text-xs font-semibold text-gray-600 mb-1.5"
                >
                  To confirm, type <span className="font-mono text-red-600 font-bold">DELETE MY ACCOUNT</span>:
                </label>
                <input
                  id="delete-confirm-input"
                  type="text"
                  value={deleteConfirmationText}
                  onChange={(e) => setDeleteConfirmationText(e.target.value)}
                  placeholder="DELETE MY ACCOUNT"
                  className="w-full px-3.5 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm font-mono text-[#0a1b33] focus:bg-white focus:outline-none focus:ring-2 focus:ring-red-500/20 focus:border-red-500 transition-all"
                />
              </div>

              <div className="mt-6 flex flex-col sm:flex-row gap-2.5 sm:justify-end">
                <button
                  type="button"
                  disabled={deleteLoading}
                  onClick={() => setDeleteModalOpen(false)}
                  className="px-4 py-2.5 rounded-full text-xs font-medium text-gray-600 hover:bg-gray-100 transition-colors cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="button"
                  disabled={
                    deleteLoading ||
                    deleteConfirmationText.trim().toUpperCase() !== 'DELETE MY ACCOUNT'
                  }
                  onClick={handleDeleteAccount}
                  className="px-5 py-2.5 rounded-full text-xs font-semibold bg-red-600 hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed text-white transition-all cursor-pointer shadow-xs flex items-center justify-center gap-2"
                >
                  {deleteLoading ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      Deleting Account...
                    </>
                  ) : (
                    'Permanently Delete Account'
                  )}
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}
