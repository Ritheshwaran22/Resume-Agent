import React from 'react';

export default function Sidebar({ activeTab, setActiveTab, isBackendHealthy }) {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: '📊', badge: 'Phase 1' },
    { id: 'upload', label: 'Upload Resume', icon: '📄', badge: 'Phase 4' },
    { id: 'job', label: 'Job Description', icon: '💼', badge: 'Phase 5' },
    { id: 'analysis', label: 'AI Analysis', icon: '⚡', badge: 'Phase 7' },
    { id: 'history', label: 'History', icon: '🕒', badge: 'Phase 10' },
  ];

  return (
    <aside className="desktop-sidebar" aria-label="Main Navigation">
      <div className="sidebar-brand">
        <div className="brand-logo">
          <span className="logo-spark">✨</span>
        </div>
        <div className="brand-text">
          <span className="brand-title">Resume Agent</span>
          <span className="brand-tag">AI Career Platform</span>
        </div>
      </div>

      <div className="sidebar-status-banner">
        <span className={`status-indicator-dot ${isBackendHealthy ? 'online' : 'checking'}`}></span>
        <div className="status-banner-text">
          <span className="status-banner-title">
            {isBackendHealthy ? 'API Connected' : 'Checking API...'}
          </span>
          <span className="status-banner-desc">Django 5.2 • Port 8000</span>
        </div>
      </div>

      <nav className="sidebar-nav">
        <span className="nav-section-title">Navigation</span>
        {navItems.map((item) => (
          <button
            key={item.id}
            onClick={() => setActiveTab(item.id)}
            className={`sidebar-nav-item ${activeTab === item.id ? 'active' : ''}`}
            type="button"
          >
            <span className="nav-icon">{item.icon}</span>
            <span className="nav-label">{item.label}</span>
            {item.badge && <span className="nav-badge">{item.badge}</span>}
          </button>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div className="system-pill">
          <span>Mobile &amp; PC Ready</span>
        </div>
        <p className="sidebar-version">v1.0.0 • Responsive Architecture</p>
      </div>
    </aside>
  );
}
