import React, { useState } from 'react';
import { authApi } from '../../data/api';

function Verify({ onLoginSuccess, onNavigate }) {
  const [code, setCode] = useState('');
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const user = await authApi.verify(code);
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
        <h1 className="profile-title" style={{ fontSize: '2.3rem' }}>Подтверждение почты</h1>
        <p className="profile-subtitle">Введите 6-значный код, отправленный на ваш Email</p>
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
            <label htmlFor="code" style={{ textAlign: 'center', display: 'block', width: '100%' }}>
              Код верификации
            </label>
            <input 
              type="text" 
              id="code" 
              required 
              maxLength="6"
              value={code}
              onChange={(e) => setCode(e.target.value.replace(/\D/g, ''))}
              className="form-input" 
              placeholder="000000" 
              style={{
                textAlign: 'center',
                fontSize: '1.8rem',
                letterSpacing: '8px',
                fontWeight: 'bold'
              }}
            />
          </div>

          <button type="submit" disabled={loading || code.length !== 6} className="btn-submit" style={{ width: '100%' }}>
            {loading ? 'Подтверждение...' : 'Подтвердить почту'}
          </button>
        </form>

        <div style={{ marginTop: '30px', borderTop: '1px solid rgba(255,255,255,0.05)', paddingTop: '20px', textAlign: 'center', fontSize: '0.8rem', color: '#718096', lineHeight: '1.6' }}>
          Письмо с кодом может идти до 2 минут.<br />
          Если письмо не пришло, проверьте папку <span style={{ color: '#dfb743' }}>Спам</span> или{' '}
          <a 
            href="#" 
            onClick={(e) => { e.preventDefault(); onNavigate('register'); }}
            style={{ color: '#dfb743', textDecoration: 'none', fontWeight: 'bold' }}
          >
            зарегистрируйтесь заново
          </a>.
        </div>
      </div>
    </div>
  );
}

export default Verify;
