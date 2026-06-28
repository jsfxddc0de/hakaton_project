import React, { useState } from 'react';
import { authApi } from '../../data/api';

function Register({ onNavigate }) {
  const [fio, setFio] = useState('');
  const [classGroup, setClassGroup] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [phone, setPhone] = useState('');
  const [wishes, setWishes] = useState('');
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await authApi.register({
        fio,
        class_group: classGroup,
        email,
        password,
        phone,
        wishes
      });
      onNavigate('verify');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="profile-container page-profile" style={{ maxWidth: '500px', margin: '60px auto' }}>
      <div className="profile-header" style={{ textAlign: 'center', marginBottom: '25px' }}>
        <h1 className="profile-title" style={{ fontSize: '2.5rem' }}>Регистрация</h1>
        <p className="profile-subtitle">Создайте аккаунт и подайте заявку на Осенний Бал</p>
      </div>

      <div style={{
        background: 'rgba(255, 255, 255, 0.02)',
        border: '1px solid rgba(212, 175, 55, 0.15)',
        borderRadius: '16px',
        padding: '30px 40px',
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

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
          <div className="input-group">
            <label htmlFor="fio">ФИО (Обязательно)</label>
            <input 
              type="text" 
              id="fio" 
              required 
              value={fio}
              onChange={(e) => setFio(e.target.value)}
              className="form-input" 
              placeholder="Иванов Иван Иванович" 
            />
          </div>

          <div className="input-group">
            <label htmlFor="classGroup">Класс / Группа (Обязательно)</label>
            <input 
              type="text" 
              id="classGroup" 
              required 
              value={classGroup}
              onChange={(e) => setClassGroup(e.target.value)}
              className="form-input" 
              placeholder="10А класс / Оргкомитет" 
            />
          </div>

          <div className="input-group">
            <label htmlFor="email">Email (Обязательно)</label>
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
            <label htmlFor="password">Пароль (Обязательно)</label>
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

          <div className="input-group" style={{ borderTop: '1px solid rgba(255,255,255,0.05)', paddingTop: '15px' }}>
            <label htmlFor="phone">Номер телефона (Необязательно)</label>
            <input 
              type="tel" 
              id="phone" 
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              className="form-input" 
              placeholder="+7 (999) 999-99-99" 
            />
          </div>

          <div className="input-group">
            <label htmlFor="wishes">Пожелания / Вопросы (Необязательно)</label>
            <textarea 
              id="wishes" 
              value={wishes}
              onChange={(e) => setWishes(e.target.value)}
              className="form-input" 
              placeholder="Например, пожелания к музыке или партнеру..." 
              rows={2}
            />
          </div>

          <button type="submit" disabled={loading} className="btn-submit" style={{ width: '100%', marginTop: '10px' }}>
            {loading ? 'Отправка...' : 'Зарегистрироваться'}
          </button>
        </form>

        <p style={{ marginTop: '20px', textAlign: 'center', fontSize: '0.85rem', color: '#a0aec0' }}>
          Уже есть аккаунт?{' '}
          <a 
            href="#" 
            onClick={(e) => { e.preventDefault(); onNavigate('login'); }}
            style={{ color: '#dfb743', textDecoration: 'none', fontWeight: 'bold' }}
          >
            Войти
          </a>
        </p>
      </div>
    </div>
  );
}

export default Register;
