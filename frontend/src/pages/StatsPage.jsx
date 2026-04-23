import React, { useEffect, useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';

const StatsPage = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('http://localhost:8000/stats')
      .then(r => r.json())
      .then(data => { setStats(data); setLoading(false); })
      .catch(() => setLoading(false));
  }, []);

  const localQuestions = parseInt(localStorage.getItem('total_questions_asked') || '0');

  // Build 7-day activity chart data from all user sessions in localStorage
  const buildActivityData = () => {
    const days = [];
    for (let i = 6; i >= 0; i--) {
      const d = new Date(); d.setDate(d.getDate() - i);
      days.push({ label: d.toLocaleDateString('en', { weekday: 'short' }), dateStr: d.toDateString(), count: 0 });
    }
    Object.keys(localStorage).forEach(key => {
      if (!key.startsWith('qa_sessions_')) return;
      const sessions = JSON.parse(localStorage.getItem(key) || '[]');
      sessions.forEach(session => {
        session.messages?.forEach(msg => {
          if (msg.sender !== 'user') return;
          const msgDate = new Date(msg.timestamp || session.created_at).toDateString();
          const day = days.find(d => d.dateStr === msgDate);
          if (day) day.count++;
        });
      });
    });
    return days;
  };

  // Top-10 questions
  const buildTopQuestions = () => {
    const freq = {};
    Object.keys(localStorage).forEach(key => {
      if (!key.startsWith('qa_sessions_')) return;
      const sessions = JSON.parse(localStorage.getItem(key) || '[]');
      sessions.forEach(session => {
        session.messages?.forEach(msg => {
          if (msg.sender !== 'user') return;
          const q = msg.text?.trim();
          if (q) freq[q] = (freq[q] || 0) + 1;
        });
      });
    });
    return Object.entries(freq).sort((a, b) => b[1] - a[1]).slice(0, 10);
  };

  const activityData = buildActivityData();
  const topQuestions = buildTopQuestions();

  if (loading) return (
    <div className="stats-page">
      <div className="stats-loading">Loading statistics...</div>
    </div>
  );

  return (
    <div className="stats-page">
      <div className="stats-container">
        <div className="nav-header">
          <Link to="/dashboard" className="back-link">← Back to Dashboard</Link>
        </div>
        <div className="stats-header">
          <h1 className="stats-title">📊 System Analytics</h1>
          <p className="stats-subtitle">Live performance metrics for the QA Knowledge Engine</p>
        </div>

        {/* KPI Cards */}
        <div className="stats-kpi-grid">
          <div className="stats-kpi-card primary">
            <div className="kpi-icon">🧠</div>
            <div className="kpi-value">{stats?.total_records || '—'}</div>
            <div className="kpi-label">Training Records</div>
          </div>
          <div className="stats-kpi-card indigo">
            <div className="kpi-icon">📖</div>
            <div className="kpi-value">{stats?.vocabulary_size || '—'}</div>
            <div className="kpi-label">Vocabulary Size</div>
          </div>
          <div className="stats-kpi-card purple">
            <div className="kpi-icon">📁</div>
            <div className="kpi-value">{stats?.dataset_size_mb || '—'} MB</div>
            <div className="kpi-label">Dataset Storage</div>
          </div>
          <div className="stats-kpi-card yellow">
            <div className="kpi-icon">👥</div>
            <div className="kpi-value">{stats?.total_users || '—'}</div>
            <div className="kpi-label">Registered Users</div>
          </div>
          <div className="stats-kpi-card orange">
            <div className="kpi-icon">⚡</div>
            <div className="kpi-value">{stats?.latency_ms || '—'}ms</div>
            <div className="kpi-label">Avg Response Time</div>
          </div>
        </div>

        {/* Domain Breakdown */}
        {stats?.domains && (
          <div className="stats-card">
            <h2 className="stats-section-title">Knowledge Domain Breakdown</h2>
            <div className="domain-grid">
              {stats.domains.map((domain) => {
                const displayVal = domain.value;
                return (
                  <div key={domain.name} className="domain-row">
                    <div className="domain-info">
                      <span className="domain-name">{domain.name}</span>
                      <span className="domain-count">{displayVal} coverage</span>
                    </div>
                    <div className="domain-bar-bg">
                      <div className="domain-bar-fill" style={{ width: displayVal }}></div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Activity Chart */}
        <div className="stats-card">
          <h2 className="stats-section-title">📅 Questions Asked — Last 7 Days</h2>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={activityData} margin={{ top: 8, right: 8, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9"/>
              <XAxis dataKey="label" tick={{ fontSize: 12, fill: '#94a3b8' }}/>
              <YAxis tick={{ fontSize: 12, fill: '#94a3b8' }} allowDecimals={false}/>
              <Tooltip contentStyle={{ borderRadius: '10px', fontSize: '0.85rem', border: '1px solid #e2e8f0' }}/>
              <Bar dataKey="count" fill="#6366f1" radius={[6,6,0,0]} name="Questions"/>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Top Questions */}
        {topQuestions.length > 0 && (
          <div className="stats-card">
            <h2 className="stats-section-title">🔥 Most Asked Questions</h2>
            <div className="top-questions-list">
              {topQuestions.map(([q, count], i) => (
                <div key={i} className="top-question-row">
                  <span className="top-q-rank">#{i + 1}</span>
                  <span className="top-q-text">{q.length > 80 ? q.substring(0, 80) + '…' : q}</span>
                  <span className="top-q-badge">{count}×</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Model Info */}
        <div className="stats-card">
          <h2 className="stats-section-title">Model Information</h2>
          <div className="model-info-grid">
            <div className="model-info-item">
              <span className="model-info-label">Architecture</span>
              <span className="model-info-value">TF-IDF + Cosine Similarity</span>
            </div>
            <div className="model-info-item">
              <span className="model-info-label">Input Processing</span>
              <span className="model-info-value">Lemmatization + Stopword Removal</span>
            </div>
            <div className="model-info-item">
              <span className="model-info-label">Retrieval Method</span>
              <span className="model-info-value">Nearest Neighbor (Vectorized)</span>
            </div>
            <div className="model-info-item">
              <span className="model-info-label">Confidence Threshold</span>
              <span className="model-info-value">0.15</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StatsPage;
