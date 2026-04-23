import React from 'react';
import { useNavigate } from 'react-router-dom';
import SidebarSessions from './SidebarSessions';
import SidebarProfile from './SidebarProfile';
import { Settings, BarChart3, LogOut, Zap } from 'lucide-react';

const Sidebar = ({ isCollapsed, onNewChat, onLogout, user, sessions, activeSessionId, onSelectSession, onDeleteSession }) => {
  const navigate = useNavigate();

  return (
    <aside className={`sidebar ${isCollapsed ? 'collapsed' : ''}`}>
      <div className="sidebar-header">
        <div className="logo-icon">QA</div>
        {!isCollapsed && (
          <div className="sidebar-title-group">
            <span className="sidebar-title">Knowledge Assistant</span>
            {user?.role === 'admin' && <span className="admin-role-badge">ADMIN</span>}
          </div>
        )}
      </div>

      <div className="chat-history">
        {!isCollapsed ? (
          <SidebarSessions
            sessions={sessions}
            activeSessionId={activeSessionId}
            onSelectSession={onSelectSession}
            onNewChat={onNewChat}
            onDeleteSession={onDeleteSession}
            user={user}
          />
        ) : (
          <div className="collapsed-sessions">
            <button className="collapsed-new-chat" onClick={onNewChat} title="New Chat">+</button>
          </div>
        )}
      </div>

      {!isCollapsed && (
        <div className="sidebar-footer">
          <SidebarProfile user={user} />
          
          <div className="sidebar-footer-actions">
            {user?.role === 'admin' && (
              <button className="footer-action-btn" onClick={() => navigate('/admin')}>
                <Settings size={16} />
                <span>Admin Panel</span>
              </button>
            )}

            <button className="footer-action-btn" onClick={() => navigate('/architecture')}>
              <Settings size={16} />
              <span>Architecture</span>
            </button>
            <button className="footer-action-btn" onClick={() => navigate('/stats')}>
              <BarChart3 size={16} />
              <span>System Analytics</span>
            </button>
            <button className="footer-action-btn logout" onClick={onLogout}>
              <LogOut size={16} />
              <span>Logout Session</span>
            </button>
          </div>
        </div>
      )}
    </aside>
  );
};

export default Sidebar;
