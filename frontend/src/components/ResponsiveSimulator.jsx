import React from 'react';

export default function ResponsiveSimulator({ simulatedWidth, setSimulatedWidth }) {
  const breakpoints = [
    { label: '360px', width: '360px', tag: 'Android Compact' },
    { label: '390px', width: '390px', tag: 'iPhone' },
    { label: '412px', width: '412px', tag: 'Pixel / Android' },
    { label: '768px', width: '768px', tag: 'Tablet' },
    { label: '1024px', width: '1024px', tag: 'Laptop' },
    { label: '1440px', width: '1440px', tag: 'Desktop' },
    { label: 'Fluid', width: '100%', tag: 'Full Window' },
  ];

  return (
    <div className="simulator-bar" role="region" aria-label="Responsive Device Preview Bar">
      <div className="simulator-title">
        <span className="simulator-icon">📐</span>
        <span className="simulator-label">Responsive Preview:</span>
      </div>

      <div className="simulator-buttons">
        {breakpoints.map((bp) => (
          <button
            key={bp.label}
            type="button"
            className={`simulator-btn ${simulatedWidth === bp.width ? 'active' : ''}`}
            onClick={() => setSimulatedWidth(bp.width)}
            title={`${bp.tag} (${bp.label})`}
          >
            <span className="btn-size">{bp.label}</span>
            <span className="btn-tag">{bp.tag}</span>
          </button>
        ))}
      </div>

      <div className="simulator-current">
        Active Width: <strong>{simulatedWidth === '100%' ? 'Auto (100% Fluid)' : simulatedWidth}</strong>
      </div>
    </div>
  );
}
