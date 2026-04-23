import React from 'react';

const getDateGroup = (isoString) => {
  const now = new Date();
  const date = new Date(isoString);
  const diffMs = now - date;
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

  if (diffDays === 0) return 'Today';
  if (diffDays === 1) return 'Yesterday';
  if (diffDays <= 7) return 'Previous 7 Days';
  return 'Older';
};

const SidebarSessions = ({ sessions, activeSessionId, onSelectSession, onNewChat, onDeleteSession, user }) => {
  // Group sessions by date
  const groups = {};
  const ORDER = ['Today', 'Yesterday', 'Previous 7 Days', 'Older'];

  sessions.forEach(session => {
    const label = getDateGroup(session.last_updated || session.created_at);
    if (!groups[label]) groups[label] = [];
    groups[label].push(session);
  });

  return (
    <div className="sidebar-sessions">
      <button className="new-chat-btn" onClick={onNewChat} title="Start a new conversation">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
          <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
        </svg>
        New Chat
      </button>

      <div className="sessions-list-container">
        {ORDER.filter(g => groups[g]).map(groupName => (
          <div key={groupName} className="session-group">
            <span className="session-group-label">{groupName}</span>
            {groups[groupName].map(session => (
              <div
                key={session.id}
                className={`session-item ${activeSessionId === session.id ? 'active' : ''}`}
                onClick={() => onSelectSession(session.id)}
              >
                <div className="session-info">
                  <svg className="chat-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
                  </svg>
                  <span className="session-title" title={session.title}>
                    {session.title}
                  </span>
                </div>
                <button
                  className="delete-session-btn"
                  onClick={e => { e.stopPropagation(); onDeleteSession(session.id); }}
                  title="Delete chat"
                >
                  ×
                </button>
              </div>
            ))}
          </div>
        ))}

        {sessions.length === 0 && (
          <div className="empty-sessions">No conversations yet</div>
        )}
      </div>
    </div>
  );
};

export default SidebarSessions;
