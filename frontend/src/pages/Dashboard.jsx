import React, { useState } from 'react';
import Sidebar from '../components/Sidebar';
import Header from '../components/Header';
import ChatWindow from '../components/ChatWindow';
import ChatInput from '../components/ChatInput';
import toast from 'react-hot-toast';
import jsPDF from 'jspdf';

const Dashboard = ({ 
  user, sessions, activeSessionId, messages, 
  onSendMessage, onNewChat, onSelectSession, onDeleteSession,
  isLoading, onLogout, onRegenerate,
  theme, toggleTheme
}) => {
  const [isSidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [input, setInput] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [showSearch, setShowSearch] = useState(false);

  const handleSend = () => {
    if (input.trim()) {
      onSendMessage(input);
      setInput('');
    }
  };

  // Export chat as TXT
  const exportTxt = () => {
    const lines = messages.map(m => `[${m.sender.toUpperCase()}]: ${m.text}`).join('\n\n');
    const blob = new Blob([lines], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a'); a.href = url; a.download = 'chat-export.txt'; a.click();
    URL.revokeObjectURL(url);
    toast.success('Chat exported as TXT!');
  };

  // Export chat as PDF
  const exportPdf = () => {
    const doc = new jsPDF();
    let y = 20;
    doc.setFont('helvetica', 'bold');
    doc.setFontSize(14);
    doc.text('Chat Export — Knowledge Assistant', 14, y);
    y += 10;
    doc.setFontSize(9);
    doc.setFont('helvetica', 'normal');
    messages.forEach(m => {
      if (m.sender === 'code') return;
      const label = m.sender === 'user' ? 'You' : 'Assistant';
      doc.setFont('helvetica', 'bold');
      doc.text(`${label}:`, 14, y);
      y += 5;
      doc.setFont('helvetica', 'normal');
      const lines = doc.splitTextToSize(m.text || '', 180);
      doc.text(lines, 14, y);
      y += lines.length * 5 + 6;
      if (y > 270) { doc.addPage(); y = 20; }
    });
    doc.save('chat-export.pdf');
    toast.success('Chat exported as PDF!');
  };

  // Search results across sessions
  const searchResults = searchQuery.trim().length > 1
    ? sessions.flatMap(s => 
        s.messages
          .filter(m => m.text?.toLowerCase().includes(searchQuery.toLowerCase()))
          .map(m => ({ sessionTitle: s.title, sessionId: s.id, text: m.text, sender: m.sender }))
      )
    : [];

  return (
    <div className={`dashboard-layout ${isSidebarCollapsed ? 'sidebar-collapsed' : ''}`}>
      <Sidebar
        isCollapsed={isSidebarCollapsed}
        toggleSidebar={() => setSidebarCollapsed(!isSidebarCollapsed)}
        onNewChat={onNewChat}
        onLogout={onLogout}
        user={user}
        sessions={sessions}
        activeSessionId={activeSessionId}
        onSelectSession={onSelectSession}
        onDeleteSession={onDeleteSession}
      />

      <main className="main-workspace">
        <div className={`thinking-progress-bar ${isLoading ? 'active' : ''}`}></div>
        <Header user={user} theme={theme} toggleTheme={toggleTheme} />

        {/* Toolbar: Search + Export */}
        <div className="chat-toolbar">
          <div className="toolbar-left">
            <button className="toolbar-btn" onClick={() => { setShowSearch(!showSearch); setSearchQuery(''); }} title="Search chats">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
            </button>
          </div>
          <div className="toolbar-right">
            <div className="toolbar-group">
              <button className="toolbar-btn" onClick={exportTxt} title="Export as TXT" disabled={messages.length <= 1}>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
                <span>TXT</span>
              </button>
              <button className="toolbar-btn" onClick={exportPdf} title="Export as PDF" disabled={messages.length <= 1}>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
                <span>PDF</span>
              </button>
            </div>
          </div>
        </div>

        {/* Search Panel */}
        {showSearch && (
          <div className="search-panel">
            <input
              className="search-input"
              placeholder="Search across all conversations…"
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
              autoFocus
            />
            {searchQuery.length > 1 && (
              <div className="search-results">
                {searchResults.length === 0 ? (
                  <div className="search-empty">No results found.</div>
                ) : (
                  searchResults.map((r, i) => (
                    <div key={i} className="search-result-item" onClick={() => { onSelectSession(r.sessionId); setShowSearch(false); setSearchQuery(''); }}>
                      <span className="search-result-chat">{r.sessionTitle}</span>
                      <span className="search-result-text">{r.text.substring(0, 120)}{r.text.length > 120 ? '…' : ''}</span>
                    </div>
                  ))
                )}
              </div>
            )}
          </div>
        )}

        <ChatWindow 
          messages={messages} 
          isLoading={isLoading}
          onRegenerate={onRegenerate}
          theme={theme}
        />

        <div className="input-area-fixed">
          <ChatInput
            input={input}
            setInput={setInput}
            onSend={handleSend}
            isLoading={isLoading}
            session_id={activeSessionId}
          />
        </div>
      </main>
    </div>
  );
};

export default Dashboard;
