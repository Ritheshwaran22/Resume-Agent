import React, { useState } from 'react';

export default function MobileNav({ activeTab, setActiveTab, isBackendHealthy }) {
  const [drawerOpen, setDrawerOpen] = useState(false);

  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: '📊' },
    { id: 'upload', label: 'Upload', icon: '📄' },
    { id: 'job', label: 'Job Desc', icon: '💼' },
    { id: 'analysis', label: 'Analyze', icon: '⚡' },
    { id: 'history', label: 'History', icon: '🕒' },
  ];

  const handleSelectTab = (id) => {
    setActiveTab(id);
    setDrawerOpen(false);
  };

  return (
    <>
      {/* Mobile Top App Bar */}
      <header className="mobile-top-bar">
        <div className="mobile-brand">
          <div className="mobile-brand-icon">✨</div>
          <span className="mobile-brand-title">Resume Agent</span>
        </div>

        <div className="mobile-top-actions">
          <span
            className={`mobile-health-chip ${isBackendHealthy ? 'online' : 'offline'}`}
            title={isBackendHealthy ? 'Backend API Online' : 'Connecting to API'}
          >
            <span className="dot"></span>
            {isBackendHealthy ? 'API Live' : 'API Offline'}
          </span>

          <button
            type="button"
            className="mobile-menu-btn"
            onClick={() => setDrawerOpen(!drawerOpen)}
            aria-label="Toggle navigation drawer"
            aria-expanded={drawerOpen}
          >
            {drawerOpen ? '✕' : '☰'}
          </button>
        </div>
      </header>

      {/* Slide-over Drawer Backdrop */}
      {drawerOpen && (
        <div
          className="drawer-backdrop"
          onClick={() => setDrawerOpen(false)}
          aria-hidden="true"
        />
      )}

      {/* Slide-over Mobile Drawer */}
      <aside className={`mobile-drawer ${drawerOpen ? 'open' : ''}`} aria-label="Mobile Navigation Drawer">
        <div className="drawer-header">
          <div className="mobile-brand">
            <div className="mobile-brand-icon">✨</div>
            <span className="mobile-brand-title">AI Resume Agent</span>
          </div>
          <button
            type="button"
            className="drawer-close-btn"
            onClick={() => setDrawerOpen(false)}
            aria-label="Close menu"
          >
            ✕
          </button>
        </div>

        <div className="drawer-body">
          <p className="drawer-section-title">Navigation</p>
          <div className="drawer-links">
            {navItems.map((item) => (
              <button
                key={item.id}
                onClick={() => handleSelectTab(item.id)}
                className={`drawer-link ${activeTab === item.id ? 'active' : ''}`}
                type="button"
              >
                <span className="drawer-link-icon">{item.icon}</span>
                <span className="drawer-link-label">{item.label}</span>
              </button>
            ))}
          </div>

          <div className="drawer-info-box">
            <p className="drawer-info-title">📱 Mobile Experience</p>
            <p className="drawer-info-desc">
              Designed with 48px minimum touch targets, fluid layouts, and native Android/iOS APK wrapping compatibility.
            </p>
          </div>
        </div>
      </aside>

      {/* Bottom Thumb Navigation Bar (for one-handed mobile phone ergonomics) */}
      <nav className="mobile-bottom-nav" aria-label="Quick Phone Navigation">
        {navItems.map((item) => (
          <button
            key={item.id}
            onClick={() => handleSelectTab(item.id)}
            className={`bottom-nav-item ${activeTab === item.id ? 'active' : ''}`}
            type="button"
          >
            <span className="bottom-nav-icon">{item.icon}</span>
            <span className="bottom-nav-label">{item.label}</span>
          </button>
        ))}
      </nav>
    </>
  );
}
