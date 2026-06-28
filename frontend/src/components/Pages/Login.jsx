import React, { useState } from 'react';
import { authApi } from '../../data/api';

function Login({ onLoginSuccess, onNavigate }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const user = await authApi.login(email, password);
      onLoginSuccess(user);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="profile-container page-profile" style={{ maxWidth: '450px', margin: '80px auto' }}>
      <div className="profile-header" style={{ textAlign: 'center', marginBottom: '30px' }}>
        <h1 className="profile-title" style={{ fontSize: '2.5rem' }}>Вход</h1>
        <p className="profile-subtitle">Войдите в личный кабинет участника бала</p>
      </div>

      <div style={{
        background: 'rgba(255, 255, 255, 0.02)',
        border: '1px solid rgba(212, 175, 55, 0.15)',
        borderRadius: '16px',
        padding: '40px',
        boxShadow: '0 15px 35px rgba(0, 0, 0, 0.2)'
      }}>
        {error && (
          <div style={{
            backgroundColor: 'rgba(245, 101, 101, 0.15)',
            color: '#f56565',
            border: '1px solid rgba(245, 101, 101, 0.3)',
            padding: '12px',
            borderRadius: '8px',
            fontSize: '0.85rem',
            textAlign: 'center',
            marginBottom: '20px'
          }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <div className="input-group">
            <label htmlFor="email">Электронная почта (Email)</label>
            <input 
              type="email" 
              id="email" 
              required 
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="form-input" 
              placeholder="example@mail.ru" 
            />
          </div>

          <div className="input-group">
            <label htmlFor="password">Пароль</label>
            <input 
              type="password" 
              id="password" 
              required 
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="form-input" 
              placeholder="••••••••" 
            />
          </div>

          <button type="submit" disabled={loading} className="btn-submit" style={{ width: '100%' }}>
            {loading ? 'Вход...' : 'Войти'}
          </button>
        </form>

        <p style={{ marginTop: '24px', textAlign: 'center', fontSize: '0.85rem', color: '#a0aec0' }}>
          Еще нет аккаунта?{' '}
          <a 
            href="#" 
            onClick={(e) => { e.preventDefault(); onNavigate('register'); }}
            style={{ color: '#dfb743', textDecoration: 'none', fontWeight: 'bold' }}
          >
            Создать аккаунт
          </a>
        </p>
      </div>
    </div>
  );
}

export default Login;
