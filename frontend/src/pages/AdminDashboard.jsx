import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';

const AdminDashboard = ({ user }) => {
  const [users, setUsers] = useState([]);
  const [feedback, setFeedback] = useState([]);
  const [resetForm, setResetForm] = useState({ username: '', newPassword: '' });
  const [message, setMessage] = useState('');
  const [activeTab, setActiveTab] = useState('users');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchUsers();
    fetchFeedback();
  }, []);

  const fetchUsers = async () => {
    try {
      const res = await fetch('http://localhost:8000/admin/users');
      const data = await res.json();
      setUsers(data);
    } catch {
      setMessage('Failed to load users');
    } finally {
      setLoading(false);
    }
  };

  const fetchFeedback = async () => {
    try {
      const res = await fetch('http://localhost:8000/admin/feedback');
      const data = await res.json();
      setFeedback(data);
    } catch {}
  };

  const handleReset = async (e) => {
    e.preventDefault();
    if (!resetForm.username || !resetForm.newPassword) return;
    try {
      const res = await fetch('http://localhost:8000/admin/reset-password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: resetForm.username,
          new_password: resetForm.newPassword,
          admin_username: user?.username
        })
      });
      const data = await res.json();
      setMessage(res.ok ? `✅ ${data.message}` : `❌ ${data.detail}`);
      setResetForm({ username: '', newPassword: '' });
      if (res.ok) fetchUsers();
    } catch {
      setMessage('❌ Network error');
    }
    setTimeout(() => setMessage(''), 4000);
  };

  const handleDelete = async (username) => {
    if (!window.confirm(`Are you sure you want to delete user "${username}"? This action cannot be undone.`)) return;
    try {
      const res = await fetch(`http://localhost:8000/admin/user/${username}?admin_username=${user?.username}`, {
        method: 'DELETE'
      });
      const data = await res.json();
      if (res.ok) {
        setMessage(`✅ ${data.message}`);
        fetchUsers();
      } else {
        setMessage(`❌ ${data.detail}`);
      }
    } catch {
      setMessage('❌ Network error');
    }
    setTimeout(() => setMessage(''), 4000);
  };

  const thumbCount = (rating) => feedback.filter(f => f.rating === rating).length;

  return (
    <div className="admin-page">
      <div className="admin-container">
        <div className="nav-header">
          <Link to="/dashboard" className="back-link">← Back to Dashboard</Link>
        </div>
        <div className="admin-header">
          <div className="admin-title-row">
            <span className="admin-icon">⚙️</span>
            <div>
              <h1 className="admin-title">Admin Dashboard</h1>
              <p className="admin-subtitle">Manage users and monitor feedback</p>
            </div>
          </div>
          <div className="admin-badge">ADMIN</div>
        </div>

        {/* Stats row */}
        <div className="admin-stats-row">
          <div className="admin-stat-card">
            <span className="admin-stat-num">{users.length}</span>
            <span className="admin-stat-label">Total Users</span>
          </div>
          <div className="admin-stat-card">
            <span className="admin-stat-num">{users.filter(u => u.role === 'admin').length}</span>
            <span className="admin-stat-label">Admins</span>
          </div>
          <div className="admin-stat-card green">
            <span className="admin-stat-num">{thumbCount('up')}</span>
            <span className="admin-stat-label">👍 Positive</span>
          </div>
          <div className="admin-stat-card red">
            <span className="admin-stat-num">{thumbCount('down')}</span>
            <span className="admin-stat-label">👎 Negative</span>
          </div>
        </div>

        {/* Tabs */}
        <div className="admin-tabs">
          {['users', 'reset', 'feedback'].map(tab => (
            <button
              key={tab}
              className={`admin-tab ${activeTab === tab ? 'active' : ''}`}
              onClick={() => setActiveTab(tab)}
            >
              {tab === 'users' ? '👥 Users' : tab === 'reset' ? '🔑 Reset Password' : '💬 Feedback'}
            </button>
          ))}
        </div>

        {message && <div className="admin-message">{message}</div>}

        {/* Users Tab */}
        {activeTab === 'users' && (
          <div className="admin-card">
            <h2 className="admin-section-title">Registered Users</h2>
            {loading ? (
              <p className="admin-loading">Loading...</p>
            ) : (
              <table className="admin-table">
                <thead>
                  <tr>
                    <th>#</th>
                    <th>Username</th>
                    <th>Role</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map((u, i) => (
                    <tr key={u.username}>
                      <td>{i + 1}</td>
                      <td><strong>{u.username}</strong></td>
                      <td>
                        <span className={`role-badge ${u.role}`}>{u.role.toUpperCase()}</span>
                      </td>
                      <td>
                        <div className="admin-actions">
                          <button
                            className="quick-reset-btn"
                            onClick={() => { setResetForm(p => ({ ...p, username: u.username })); setActiveTab('reset'); }}
                          >
                            Reset Password
                          </button>
                          {u.username !== "Admin" && u.username !== user?.username && (
                            <button
                              className="delete-user-btn"
                              onClick={() => handleDelete(u.username)}
                            >
                              Delete
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        )}

        {/* Reset Tab */}
        {activeTab === 'reset' && (
          <div className="admin-card">
            <h2 className="admin-section-title">Security & Password Reset</h2>
            <div className="admin-form-container">
              <form className="admin-form" onSubmit={handleReset}>
                <p className="form-info-text">Enter the username of the account you wish to reset and provide a new secure password.</p>
                <div className="admin-field">
                  <label>Username</label>
                  <input
                    type="text"
                    placeholder="e.g. Yash"
                    value={resetForm.username}
                    onChange={e => setResetForm(p => ({ ...p, username: e.target.value }))}
                  />
                </div>
                <div className="admin-field">
                  <label>New Password</label>
                  <input
                    type="password"
                    placeholder="••••••••"
                    value={resetForm.newPassword}
                    onChange={e => setResetForm(p => ({ ...p, newPassword: e.target.value }))}
                  />
                </div>
                <button type="submit" className="admin-submit-btn">Update Password</button>
              </form>
            </div>
          </div>
        )}

        {/* Feedback Tab */}
        {activeTab === 'feedback' && (
          <div className="admin-card">
            <h2 className="admin-section-title">User Feedback ({feedback.length} entries)</h2>
            {feedback.length === 0 ? (
              <p className="admin-loading">No feedback submitted yet.</p>
            ) : (
              <div className="feedback-list">
                {[...feedback].reverse().slice(0, 50).map((f, i) => (
                  <div key={i} className={`feedback-item ${f.rating}`}>
                    <div className="feedback-meta">
                      <div className="feedback-meta-left">
                        <span className="feedback-rating">{f.rating === 'up' ? '👍' : '👎'}</span>
                        <span className="feedback-user">{f.username}</span>
                      </div>
                      <span className="feedback-time">{new Date(f.timestamp).toLocaleString()}</span>
                    </div>
                    <div className="feedback-content">
                      <div className="feedback-q-row">
                        <span className="feedback-label">Q:</span>
                        <span className="feedback-text">{f.question || <em style={{opacity: 0.5}}>(Empty or Greeting)</em>}</span>
                      </div>
                      <div className="feedback-a-row">
                        <span className="feedback-label">A:</span>
                        <span className="feedback-text">{f.answer}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminDashboard;
