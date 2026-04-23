import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { User, Mail, Lock, UserPlus, ArrowRight } from 'lucide-react';

const Register = () => {
  const [formData, setFormData] = useState({
    fullName: '',
    username: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: formData.username,
          password: formData.password
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Registration failed');
      }

      alert('Registration successful! Please login.');
      navigate('/login');
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card neon-card-premium registration-card">
        <div className="auth-header">
          <div className="premium-logo-box">QA</div>
          <h1 className="technical-title">Initialize Profile</h1>
          <p className="access-subtitle">Create your professional credentials</p>
        </div>
        
        <form onSubmit={handleSubmit} className="auth-form-refined">
          <div className="form-field">
            <label className="field-label-spacious">FULL NAME</label>
            <div className="recessed-input-wrapper">
              <UserPlus size={18} className="field-icon" />
              <input
                id="fullName"
                name="fullName"
                type="text"
                placeholder="e.g. John Doe"
                value={formData.fullName}
                onChange={handleChange}
                required
              />
            </div>
          </div>

          <div className="form-field">
            <label className="field-label-spacious">USERNAME</label>
            <div className="recessed-input-wrapper">
              <User size={18} className="field-icon" />
              <input
                id="username"
                name="username"
                type="text"
                placeholder="Choose a username"
                value={formData.username}
                onChange={handleChange}
                required
              />
            </div>
          </div>

          <div className="form-field">
            <label className="field-label-spacious">EMAIL</label>
            <div className="recessed-input-wrapper">
              <Mail size={18} className="field-icon" />
              <input
                id="email"
                name="email"
                type="email"
                placeholder="engineer@company.com"
                value={formData.email}
                onChange={handleChange}
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
                name="password"
                type="password"
                placeholder="Create a strong password"
                value={formData.password}
                onChange={handleChange}
                required
              />
            </div>
          </div>

          <div className="form-field">
            <label className="field-label-spacious">CONFIRM PASSWORD</label>
            <div className="recessed-input-wrapper">
              <Lock size={18} className="field-icon" />
              <input
                id="confirmPassword"
                name="confirmPassword"
                type="password"
                placeholder="Repeat your password"
                value={formData.confirmPassword}
                onChange={handleChange}
                required
              />
            </div>
          </div>
          
          {error && <div className="auth-error-vibrant">{error}</div>}
          
          <button type="submit" className="engine-access-btn" disabled={isLoading}>
            {isLoading ? 'PROCESSING...' : (
              <>Create Elite Account <ArrowRight size={18} className="btn-arrow"/></>
            )}
          </button>
        </form>
        
        <div className="auth-footer-refined">
          <p>Already have an account? <Link to="/login" className="premium-link">Login</Link></p>
        </div>
        
        <div className="signature-branding">
          ENGINEERED BY <span>YASHU</span>
        </div>
      </div>
    </div>
  );
};

export default Register;
