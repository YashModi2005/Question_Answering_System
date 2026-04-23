import React from 'react';
import { Moon, Sun } from 'lucide-react';

const Header = ({ user, theme, toggleTheme }) => {
  return (
    <header className="status-header">
      <div className="header-left">
        <div className="pill-badge indigo">
          <span className="pill-dot"></span>
          <div className="header-stat">
            <span className="stat-label">MODEL</span>
            <span className="stat-value">TF-IDF Retrieval Engine</span>
          </div>
        </div>
        <div className="pill-badge emerald">
          <span className="pill-dot"></span>
          <div className="header-stat">
            <span className="stat-label">DATASET</span>
            <span className="stat-value">600k QA Pairs</span>
          </div>
        </div>
      </div>

      <div className="header-right">
        <button 
          className="action-icon-btn theme-toggle" 
          onClick={toggleTheme} 
          title={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
          style={{ marginRight: '8px', padding: '8px', border: 'none', background: 'transparent' }}
        >
          {theme === 'light' ? <Moon size={20} /> : <Sun size={20} />}
        </button>

        <div className="status-badge">
          <span className="glowing-dot"></span>
          AI STATUS: ONLINE
        </div>
        <div className="header-operator">
          <span className="stat-label">OPERATOR</span>
          <span className="stat-value">{user?.username || 'SYSTEM ADMIN'}</span>
        </div>
      </div>
    </header>
  );
};

export default Header;
