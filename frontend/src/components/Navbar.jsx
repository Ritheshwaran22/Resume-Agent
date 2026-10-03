import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'motion/react';
import { Menu, X, ArrowRight, FileText, User, LogOut, Settings } from 'lucide-react';
import Button from './Button';
import { useAuth } from '../context/AuthContext';

export default function Navbar() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const { user, isAuthenticated, logout } = useAuth();

  const navLinks = [
    { label: 'Home', path: '/' },
    { label: 'How it works', path: '/how-it-works' },
    { label: 'Features', path: '/features' },
    { label: 'Live Preview', path: '/preview' },
  ];

  const isActive = (path) => {
    if (path === '/') {
      return location.pathname === '/';
    }
    return location.pathname.startsWith(path);
  };

  const handleLogout = () => {
    logout();
    navigate('/');
    setMobileMenuOpen(false);
  };

  return (
    <header className="fixed top-4 left-0 right-0 z-50 px-4 sm:px-6 pointer-events-none">
      <div className="max-w-[1200px] mx-auto flex items-center justify-between">
        {/* Floating Pill Nav Container */}
        <div className="w-full flex items-center justify-between px-4 py-2.5 bg-white/90 backdrop-blur-md rounded-full border border-gray-200/80 shadow-[0_2px_16px_-4px_rgba(10,27,51,0.06)] pointer-events-auto transition-all">
          {/* Logo */}
          <Link
            to="/"
            className="flex items-center gap-2.5 text-left focus-visible:outline-none group cursor-pointer"
          >
            <div className="w-8 h-8 rounded-full bg-[#0a152d] flex items-center justify-center text-white shadow-xs group-hover:scale-105 transition-transform">
              <FileText className="w-4 h-4" />
            </div>
            <div className="flex flex-col">
              <span className="font-display font-bold text-base tracking-tight text-[#0a1b33]">
                Resume Agent
              </span>
            </div>
          </Link>

          {/* Desktop Nav Items */}
          <nav className="hidden md:flex items-center gap-1 text-sm font-medium text-gray-600">
            {isAuthenticated ? (
              <>
                <Link
                  to="/dashboard"
                  className={`px-3.5 py-1.5 rounded-full transition-colors cursor-pointer ${
                    isActive('/dashboard')
                      ? 'text-[#0a1b33] bg-gray-100 font-semibold'
                      : 'hover:text-[#0a1b33] hover:bg-gray-100/70'
                  }`}
                >
                  Dashboard
                </Link>
                <Link
                  to="/resumes"
                  className={`px-3.5 py-1.5 rounded-full transition-colors cursor-pointer ${
                    isActive('/resumes')
                      ? 'text-[#0a1b33] bg-gray-100 font-semibold'
                      : 'hover:text-[#0a1b33] hover:bg-gray-100/70'
                  }`}
                >
                  My Resumes
                </Link>
                <Link
                  to="/history"
                  className={`px-3.5 py-1.5 rounded-full transition-colors cursor-pointer ${
                    isActive('/history')
                      ? 'text-[#0a1b33] bg-gray-100 font-semibold'
                      : 'hover:text-[#0a1b33] hover:bg-gray-100/70'
                  }`}
                >
                  Analysis History
                </Link>
              </>
            ) : (
              <>
                {navLinks.map((item) => {
                  const active = isActive(item.path);
                  return (
                    <Link
                      key={item.path}
                      to={item.path}
                      className={`px-3.5 py-1.5 rounded-full transition-colors cursor-pointer ${
                        active
                          ? 'text-[#0a1b33] bg-gray-100 font-semibold'
                          : 'hover:text-[#0a1b33] hover:bg-gray-100/70'
                      }`}
                    >
                      {item.label}
                    </Link>
                  );
                })}
              </>
            )}
          </nav>

          {/* Desktop Auth Controls */}
          <div className="hidden md:flex items-center gap-2">
            {isAuthenticated ? (
              <div className="flex items-center gap-2">
                <span className="flex items-center gap-1.5 px-3 py-1 bg-gray-100 text-xs font-semibold text-[#0a1b33] rounded-full">
                  <User className="w-3.5 h-3.5 text-gray-500" />
                  {user?.username}
                </span>
                <Link
                  to="/settings"
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium transition-colors cursor-pointer ${
                    isActive('/settings')
                      ? 'bg-[#0a152d] text-white font-semibold'
                      : 'text-gray-600 hover:text-[#0a1b33] hover:bg-gray-100'
                  }`}
                  title="Account Settings"
                >
                  <Settings className="w-3.5 h-3.5" />
                  <span>Settings</span>
                </Link>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleLogout}
                  icon={LogOut}
                  iconPosition="right"
                >
                  Sign out
                </Button>
              </div>
            ) : (
              <>
                <Link
                  to="/login"
                  className="text-sm font-medium px-4 py-1.5 text-gray-600 hover:text-[#0a1b33] rounded-full transition-colors cursor-pointer"
                >
                  Sign in
                </Link>
                <Button
                  variant="primary"
                  size="sm"
                  onClick={() => navigate('/register')}
                  icon={ArrowRight}
                  iconPosition="right"
                >
                  Get started
                </Button>
              </>
            )}
          </div>

          {/* Mobile Menu Toggle Button */}
          <div className="flex items-center gap-2 md:hidden">
            {isAuthenticated ? (
              <Button
                variant="primary"
                size="sm"
                onClick={() => navigate('/dashboard')}
              >
                Dashboard
              </Button>
            ) : (
              <Button
                variant="primary"
                size="sm"
                onClick={() => navigate('/login')}
              >
                Sign in
              </Button>
            )}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-1.5 text-gray-600 hover:text-[#0a1b33] rounded-full hover:bg-gray-100 focus:outline-none"
              aria-label="Toggle Navigation Menu"
            >
              {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>
      </div>


      {/* Mobile Menu Dropdown */}
      <AnimatePresence>
        {mobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.18 }}
            className="md:hidden mt-2 max-w-[1200px] mx-auto bg-white/95 backdrop-blur-md rounded-2xl border border-gray-200/90 shadow-lg p-4 pointer-events-auto"
          >
            <div className="flex flex-col gap-2">
              {isAuthenticated && (
                <div className="px-4 py-2 bg-gray-50 rounded-xl text-xs font-semibold text-[#0a1b33] flex items-center justify-between">
                  <span>Signed in as: <strong>{user?.username}</strong></span>
                </div>
              )}
              {isAuthenticated ? (
                <>
                  <Link
                    to="/dashboard"
                    onClick={() => setMobileMenuOpen(false)}
                    className={`w-full text-left px-4 py-2.5 text-sm font-medium rounded-xl transition-colors ${
                      isActive('/dashboard')
                        ? 'text-[#0a1b33] bg-gray-100 font-semibold'
                        : 'text-[#0a1b33] bg-gray-50'
                    }`}
                  >
                    Dashboard
                  </Link>
                  <Link
                    to="/resumes"
                    onClick={() => setMobileMenuOpen(false)}
                    className={`w-full text-left px-4 py-2.5 text-sm font-medium rounded-xl transition-colors ${
                      isActive('/resumes')
                        ? 'text-[#0a1b33] bg-gray-100 font-semibold'
                        : 'text-gray-700 hover:text-[#0a1b33] hover:bg-gray-50'
                    }`}
                  >
                    My Resumes
                  </Link>
                  <Link
                    to="/history"
                    onClick={() => setMobileMenuOpen(false)}
                    className={`w-full text-left px-4 py-2.5 text-sm font-medium rounded-xl transition-colors ${
                      isActive('/history')
                        ? 'text-[#0a1b33] bg-gray-100 font-semibold'
                        : 'text-gray-700 hover:text-[#0a1b33] hover:bg-gray-50'
                    }`}
                  >
                    Analysis History
                  </Link>
                  <Link
                    to="/settings"
                    onClick={() => setMobileMenuOpen(false)}
                    className={`w-full text-left px-4 py-2.5 text-sm font-medium rounded-xl transition-colors ${
                      isActive('/settings')
                        ? 'text-[#0a1b33] bg-gray-100 font-semibold'
                        : 'text-gray-700 hover:text-[#0a1b33] hover:bg-gray-50'
                    }`}
                  >
                    Account Settings
                  </Link>
                </>
              ) : (
                navLinks.map((item) => (
                  <Link
                    key={item.path}
                    to={item.path}
                    onClick={() => setMobileMenuOpen(false)}
                    className={`w-full text-left px-4 py-2.5 text-sm font-medium rounded-xl transition-colors ${
                      isActive(item.path)
                        ? 'text-[#0a1b33] bg-gray-100 font-semibold'
                        : 'text-gray-700 hover:text-[#0a1b33] hover:bg-gray-50'
                    }`}
                  >
                    {item.label}
                  </Link>
                ))
              )}
              <div className="pt-2 mt-1 border-t border-gray-100 flex flex-col gap-2">
                {isAuthenticated ? (
                  <Button
                    variant="outline"
                    size="md"
                    className="w-full justify-center"
                    onClick={handleLogout}
                    icon={LogOut}
                    iconPosition="right"
                  >
                    Sign out
                  </Button>
                ) : (
                  <>
                    <Link
                      to="/login"
                      onClick={() => setMobileMenuOpen(false)}
                      className="text-center py-2 text-sm font-semibold text-gray-700"
                    >
                      Sign In
                    </Link>
                    <Button
                      variant="primary"
                      size="md"
                      className="w-full justify-center"
                      onClick={() => {
                        navigate('/register');
                        setMobileMenuOpen(false);
                      }}
                      icon={ArrowRight}
                      iconPosition="right"
                    >
                      Get started
                    </Button>
                  </>
                )}
              </div>
            </div>

          </motion.div>
        )}
      </AnimatePresence>
    </header>
  );
}
