import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { User, Lock, ArrowRight } from 'lucide-react';

const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Authentication failed');
      }

      login(data.username, data.role);
      navigate('/dashboard');
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card neon-card-premium">
        <div className="auth-header">
          <div className="premium-logo-box">QA</div>
          <h1 className="technical-title">Technical Knowledge Assistant</h1>
          <p className="access-subtitle">Access the core intelligence engine</p>
        </div>
        
        <form onSubmit={handleSubmit} className="auth-form-refined">
          <div className="form-field">
            <label className="field-label-spacious">USERNAME</label>
            <div className="recessed-input-wrapper">
              <User size={18} className="field-icon" />
              <input
                id="username"
                type="text"
                placeholder="Enter your username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
              />
            </div>
          </div>
          
          <div className="form-field">
            <label className="field-label-spacious">PASSWORD</label>
            <div className="recessed-input-wrapper">
              <Lock size={18} className="field-icon" />
              <input
                id="password"
                type="password"
                placeholder="Enter your password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>
          </div>
          
          {error && <div className="auth-error-vibrant">{error}</div>}
          
          <button type="submit" className="engine-access-btn" disabled={isLoading}>
            {isLoading ? 'INITIATING...' : (
              <>Access Engine <ArrowRight size={18} className="btn-arrow"/></>
            )}
          </button>
        </form>
        
        <div className="auth-footer-refined">
          <p>New Engineer? <Link to="/register" className="premium-link">Create Account</Link></p>
        </div>
        
        <div className="signature-branding">
          ENGINEERED BY <span>YASHU</span>
        </div>
      </div>
    </div>
  );
};

export default Login;
