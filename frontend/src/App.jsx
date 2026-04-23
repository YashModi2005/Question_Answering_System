import React, { useState, useEffect } from 'react';
import { Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import { useAuth } from './context/AuthContext';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import AdminDashboard from './pages/AdminDashboard';
import StatsPage from './pages/StatsPage';
import ArchitectureInfo from './pages/ArchitectureInfo';
import CodeGenerator from './pages/CodeGenerator';
import './App.css';

const SESSIONS_KEY = (username) => `qa_sessions_${username}`;
const QUESTIONS_KEY = 'total_questions_asked';

function App() {
  const { user, role, isLoggedIn, logout: authLogout, loading: authLoading } = useAuth();
  const [sessions, setSessions] = useState([]);
  const [activeSessionId, setActiveSessionId] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [theme, setTheme] = useState(localStorage.getItem('theme') || 'light');
  const navigate = useNavigate();

  // Apply theme to document
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prev => prev === 'light' ? 'dark' : 'light');
  };

  // Load sessions from localStorage on login
  useEffect(() => {
    if (isLoggedIn && user) {
      const saved = JSON.parse(localStorage.getItem(SESSIONS_KEY(user)) || '[]');
      const sorted = [...saved].sort((a, b) => new Date(b.last_updated) - new Date(a.last_updated));
      
      // Always create a fresh session for a clean entry
      const newId = `session_${Date.now()}`;
      const newSession = {
        id: newId,
        title: 'New Chat',
        messages: [{ text: "Knowledge Assistant ready. Ask a technical question.", sender: 'ai', question: 'System Startup' }],
        created_at: new Date().toISOString(),
        last_updated: new Date().toISOString()
      };
      
      setSessions([newSession, ...sorted]);
      setActiveSessionId(newId);
    } else {
      setSessions([]);
      setActiveSessionId(null);
    }
  }, [isLoggedIn, user]);

  // Save sessions to localStorage whenever they change
  useEffect(() => {
    if (isLoggedIn && user && sessions.length > 0) {
      localStorage.setItem(SESSIONS_KEY(user), JSON.stringify(sessions));
    }
  }, [sessions, isLoggedIn, user]);

  const createNewSession = () => {
    const newSession = {
      id: `session_${Date.now()}`,
      title: 'New Chat',
      messages: [{ text: "Knowledge Assistant ready. Ask a technical question.", sender: 'ai', question: 'System Startup' }],
      created_at: new Date().toISOString(),
      last_updated: new Date().toISOString()
    };
    setSessions(prev => [newSession, ...prev]);
    setActiveSessionId(newSession.id);
  };

  const onSendMessage = async (text) => {
    if (!activeSessionId) return;

    const userMessage = { text, sender: 'user', timestamp: new Date().toISOString() };
    
    setIsLoading(true);

    // Update active session locally
    setSessions(prev => {
      return prev.map(session => {
        if (session.id === activeSessionId) {
          const isFirstMessage = session.messages.length <= 1;
          const newTitle = isFirstMessage 
            ? text.slice(0, 40)
            : session.title;
            
          return {
            ...session,
            title: newTitle,
            messages: [...session.messages, userMessage],
            last_updated: new Date().toISOString()
          };
        }
        return session;
      }).sort((a, b) => new Date(b.last_updated) - new Date(a.last_updated));
    });

    // Track question count for stats page
    const count = parseInt(localStorage.getItem(QUESTIONS_KEY) || '0') + 1;
    localStorage.setItem(QUESTIONS_KEY, count.toString());

    try {
      const response = await fetch("http://localhost:8000/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          question: text,
          session_id: activeSessionId 
        }),
      });

      if (!response.ok) throw new Error("Backend unreachable");

      const data = await response.json();
      const aiMessage = { 
        text: data.answer, 
        sender: 'ai', 
        question: text, 
        timestamp: new Date().toISOString(),
        confidence: data.confidence,
        confidence_level: data.confidence_level,
        matched_question: data.matched_question,
        time_taken: data.time_taken
      };
      
      const sessionUpdates = [aiMessage];

      // If the question is code-related, automatically fetch and display code
      if (data.is_coding && data.subject) {
        try {
          const codeRes = await fetch(`http://localhost:8000/code/${encodeURIComponent(data.subject)}`);
          if (codeRes.ok) {
            const codeData = await codeRes.json();
            if (codeData.code && !codeData.code.startsWith('# No specific')) {
              sessionUpdates.push({
                text: codeData.code,
                subject: codeData.subject,
                sender: 'code',
                timestamp: new Date().toISOString()
              });
            }
          }
        } catch { /* skip code fetch failure */ }
      }

      setSessions(prev => {
        const updated = prev.map(s => 
          s.id === activeSessionId 
            ? { ...s, messages: [...s.messages, ...sessionUpdates], last_updated: new Date().toISOString() }
            : s
        );
        return updated.sort((a, b) => new Date(b.last_updated) - new Date(a.last_updated));
      });

    } catch {
      const errMsg = { text: "Error: Could not connect to the backend server.", sender: 'ai', timestamp: new Date().toISOString() };
      setSessions(prev => {
        const updated = prev.map(s => 
          s.id === activeSessionId 
            ? { ...s, messages: [...s.messages, errMsg], last_updated: new Date().toISOString() }
            : s
        );
        return updated.sort((a, b) => new Date(b.last_updated) - new Date(a.last_updated));
      });
    } finally {
      setIsLoading(false);
    }
  };

  const onDeleteSession = (sessionId) => {
    setSessions(prev => {
      const filtered = prev.filter(s => s.id !== sessionId);
      if (sessionId === activeSessionId) {
        if (filtered.length > 0) setActiveSessionId(filtered[0].id);
        else setActiveSessionId(null);
      }
      return filtered;
    });
  };

  const onRenameSession = (sessionId, newTitle) => {
    setSessions(prev => prev.map(s =>
      s.id === sessionId ? { ...s, title: newTitle, last_updated: new Date().toISOString() } : s
    ).sort((a, b) => new Date(b.last_updated) - new Date(a.last_updated)));
  };

  const onRegenerate = () => {
    if (!activeSessionId) return;
    const activeSession = sessions.find(s => s.id === activeSessionId);
    if (!activeSession) return;
    // Find last user message
    const userMessages = activeSession.messages.filter(m => m.sender === 'user');
    const lastUserMsg = userMessages[userMessages.length - 1];
    if (!lastUserMsg) return;
    // Remove last AI response, then resend
    setSessions(prev => prev.map(s =>
      s.id === activeSessionId
        ? { ...s, messages: s.messages.slice(0, -1) }
        : s
    ));
    onSendMessage(lastUserMsg.text);
  };

  const handleLogout = () => {
    authLogout();
    setSessions([]);
    setActiveSessionId(null);
    navigate('/login');
  };

  if (authLoading) {
    return (
      <div className="auth-page">
        <div className="logo-icon animate-pulse" style={{ width: '64px', height: '64px', borderRadius: '12px', fontSize: '1.5rem' }}>QA</div>
      </div>
    );
  }

  const activeSession = sessions.find(s => s.id === activeSessionId);
  const userObj = { username: user, role };

  return (
    <Routes>
      <Route path="/login"    element={!isLoggedIn ? <Login />    : <Navigate to="/dashboard" />} />
      <Route path="/register" element={!isLoggedIn ? <Register /> : <Navigate to="/dashboard" />} />
      <Route path="/dashboard" element={
        isLoggedIn ? (
          <Dashboard
            user={userObj}
            sessions={sessions}
            activeSessionId={activeSessionId}
            messages={activeSession?.messages || []}
            onSendMessage={onSendMessage}
            onNewChat={createNewSession}
            onSelectSession={setActiveSessionId}
            onDeleteSession={onDeleteSession}
            onRenameSession={onRenameSession}
            onRegenerate={onRegenerate}
            isLoading={isLoading}
            onLogout={handleLogout}
            theme={theme}
            toggleTheme={toggleTheme}
          />
        ) : <Navigate to="/login" />
      } />
      <Route path="/stats" element={
        isLoggedIn ? <StatsPage /> : <Navigate to="/login" />
      } />
      <Route path="/admin" element={
        isLoggedIn && role === 'admin'
          ? <AdminDashboard user={userObj} />
          : <Navigate to={isLoggedIn ? "/dashboard" : "/login"} />
      } />
      <Route path="/architecture" element={isLoggedIn ? <ArchitectureInfo /> : <Navigate to="/login" />} />
      <Route path="/generator" element={isLoggedIn ? <CodeGenerator /> : <Navigate to="/login" />} />
      <Route path="/" element={<Navigate to={isLoggedIn ? "/dashboard" : "/login"} />} />
    </Routes>
  );
}

export default App;
