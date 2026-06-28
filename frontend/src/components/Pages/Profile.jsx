import React, { useState, useEffect } from 'react';
import { profileApi } from '../../data/api';

function Profile() {
  const [user, setUser] = useState(null);
  const [phone, setPhone] = useState('');
  const [avatar, setAvatar] = useState('');
  const [selectedEventId, setSelectedEventId] = useState('');
  const [wishes, setWishes] = useState('');
  const [loading, setLoading] = useState(true);

  const loadProfile = async () => {
    try {
      const data = await profileApi.getProfile();
      setUser(data);
      setPhone(data.phone);
      setAvatar(data.avatar);
      if (data.availableEvents.length > 0) {
        setSelectedEventId(data.availableEvents[0].id);
      } else {
        setSelectedEventId('');
      }
    } catch (e) {
      alert('Ошибка при загрузке профиля: ' + e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadProfile();
  }, []);

  const handlePhoneChange = (e) => setPhone(e.target.value);

  const handleAvatarChange = () => {
    // В реальной системе это была бы отправка файла, сейчас покажем заглушку
    alert('Для смены аватарки загрузите файл через панель настроек (в разработке)');
  };

  const handleSaveProfile = async (e) => {
    e.preventDefault();
    try {
      await profileApi.update(phone);
      alert('Профиль успешно обновлен!');
      loadProfile();
    } catch (err) {
      alert('Не удалось обновить профиль: ' + err.message);
    }
  };

  const handleApplyEvent = async (e) => {
    e.preventDefault();
    if (!selectedEventId) return;

    try {
      await profileApi.apply(Number(selectedEventId), wishes);
      alert('Заявка успешно отправлена!');
      setWishes('');
      loadProfile();
    } catch (err) {
      alert('Ошибка подачи заявки: ' + err.message);
    }
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh', color: '#dfb743', fontWeight: 'bold' }}>
        Загрузка личного кабинета...
      </div>
    );
  }

  if (!user) return null;

  return (
    <div className="profile-container page-profile">
      <div className="profile-header">
        <h1 className="profile-title">Личный Кабинет</h1>
        <p className="profile-subtitle">Управление профилем и вашими заявками на мероприятия</p>
      </div>

      <div className="profile-layout-grid" style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '30px' }}>
        {/* ЛЕВАЯ КОЛОНКА: Настройки профиля */}
        <div className="profile-card-left" style={{
          background: 'rgba(255, 255, 255, 0.02)',
          border: '1px solid rgba(212, 175, 55, 0.15)',
          borderRadius: '12px',
          padding: '30px',
          height: 'fit-content'
        }}>
          <h2 style={{ fontSize: '1.4rem', color: '#d4af37', marginBottom: '20px', fontFamily: "'Playfair Display', serif", fontWeight: 600 }}>Настройки профиля</h2>
          
          <form onSubmit={handleSaveProfile} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '10px', paddingBottom: '20px', borderBottom: '1px solid rgba(255, 255, 255, 0.05)' }}>
              <img 
                src={avatar || `https://ui-avatars.com/api/?name=${user.fullName}&background=d4af37&color=070b13&size=128`} 
                alt="Аватар" 
                style={{ width: '90px', height: '90px', borderRadius: '50%', objectFit: 'cover', border: '2px solid #d4af37', cursor: 'pointer' }}
                onClick={handleAvatarChange}
              />
              <button 
                type="button" 
                onClick={handleAvatarChange}
                style={{ background: 'none', border: 'none', color: '#d4af37', fontSize: '0.8rem', cursor: 'pointer', textDecoration: 'underline' }}
              >
                Сменить фото
              </button>
            </div>

            <div className="input-group">
              <label>ФИО</label>
              <input type="text" value={user.fullName} readOnly className="form-input" style={{ opacity: 0.6, cursor: 'not-allowed' }} />
            </div>

            <div className="input-group">
              <label>Класс / Группа</label>
              <input type="text" value={user.class_group} readOnly className="form-input" style={{ opacity: 0.6, cursor: 'not-allowed' }} />
            </div>

            <div className="input-group">
              <label>Email</label>
              <input type="text" value={user.email} readOnly className="form-input" style={{ opacity: 0.6, cursor: 'not-allowed' }} />
            </div>

            <div className="input-group">
              <label htmlFor="phone">Телефон</label>
              <input 
                type="tel" 
                id="phone" 
                value={phone} 
                onChange={handlePhoneChange} 
                className="form-input" 
                placeholder="+7 (999) 999-99-99"
              />
            </div>

            <button type="submit" className="btn-submit" style={{ width: '100%' }}>Сохранить изменения</button>
          </form>
        </div>

        {/* ПРАВАЯ КОЛОНКА: Заявки */}
        <div className="profile-content-right" style={{ display: 'flex', flexDirection: 'column', gap: '30px' }}>
          
          {/* Блок: Мои заявки */}
          <div style={{
            background: 'rgba(255, 255, 255, 0.02)',
            border: '1px solid rgba(255, 255, 255, 0.05)',
            borderRadius: '12px',
            padding: '30px'
          }}>
            <h3 style={{ fontSize: '1.4rem', color: '#d4af37', marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '10px', fontFamily: "'Playfair Display', serif" }}>
              <span>🎫</span> Мои заявки на мероприятия
            </h3>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
              {user.applications.length > 0 ? (
                user.applications.map((app) => (
                  <div key={app.id} style={{
                    background: 'rgba(0, 0, 0, 0.2)',
                    border: '1px solid rgba(255, 255, 255, 0.05)',
                    borderRadius: '8px',
                    padding: '20px',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    gap: '20px'
                  }}>
                    <div>
                      <h4 style={{ fontWeight: 'bold', color: '#ffffff', fontSize: '1.05rem', marginBottom: '5px' }}>{app.title}</h4>
                      <p style={{ fontSize: '0.85rem', color: '#a0aec0', marginBottom: '5px' }}>
                        📅 {app.date} | 📍 {app.location}
                      </p>
                      {app.wishes && (
                        <p style={{ fontSize: '0.8rem', color: '#e2e8f0', fontStyle: 'italic', borderLeft: '2px solid #d4af37', paddingLeft: '8px' }}>
                          Пожелания: "{app.wishes}"
                        </p>
                      )}
                    </div>
                    <div>
                      {app.status === 'pending' && (
                        <span style={{ backgroundColor: 'rgba(212, 175, 55, 0.15)', color: '#d4af37', border: '1px solid rgba(212, 175, 55, 0.3)', padding: '5px 12px', borderRadius: '20px', fontSize: '0.75rem', fontWeight: 'bold' }}>
                          Ожидает модерации ⏳
                        </span>
                      )}
                      {app.status === 'approved' && (
                        <span style={{ backgroundColor: 'rgba(72, 187, 120, 0.15)', color: '#48bb78', border: '1px solid rgba(72, 187, 120, 0.3)', padding: '5px 12px', borderRadius: '20px', fontSize: '0.75rem', fontWeight: 'bold' }}>
                          Одобрена ✅
                        </span>
                      )}
                      {app.status === 'rejected' && (
                        <span style={{ backgroundColor: 'rgba(245, 101, 101, 0.15)', color: '#f56565', border: '1px solid rgba(245, 101, 101, 0.3)', padding: '5px 12px', borderRadius: '20px', fontSize: '0.75rem', fontWeight: 'bold' }}>
                          Отклонена ❌
                        </span>
                      )}
                    </div>
                  </div>
                ))
              ) : (
                <p style={{ color: '#718096', textAlign: 'center', padding: '20px' }}>У вас пока нет поданных заявок.</p>
              )}
            </div>
          </div>

          {/* Блок: Запись на другие мероприятия */}
          {user.availableEvents.length > 0 && (
            <div style={{
              background: 'rgba(255, 255, 255, 0.02)',
              border: '1px solid rgba(255, 255, 255, 0.05)',
              borderRadius: '12px',
              padding: '30px'
            }}>
              <h3 style={{ fontSize: '1.4rem', color: '#d4af37', marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '10px', fontFamily: "'Playfair Display', serif" }}>
                <span>🌟</span> Записаться на другие мероприятия
              </h3>

              <form onSubmit={handleApplyEvent} style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
                <div className="input-group">
                  <label htmlFor="event-select">Выберите событие</label>
                  <select 
                    id="event-select" 
                    value={selectedEventId} 
                    onChange={(e) => setSelectedEventId(e.target.value)}
                    className="form-input"
                    style={{ background: '#070b13', color: '#fff', border: '1px solid rgba(255,255,255,0.1)' }}
                  >
                    {user.availableEvents.map(e => (
                      <option key={e.id} value={e.id}>{e.title} ({e.date})</option>
                    ))}
                  </select>
                </div>

                <div className="input-group">
                  <label htmlFor="wishes">Дополнительные пожелания (необязательно)</label>
                  <textarea 
                    id="wishes" 
                    value={wishes} 
                    onChange={(e) => setWishes(e.target.value)} 
                    className="form-input" 
                    placeholder="Например, пожелания по меню, рассадке или паре..."
                    rows={3}
                    style={{ resize: 'vertical' }}
                  />
                </div>

                <button type="submit" className="btn-submit" style={{ alignSelf: 'flex-start' }}>Подать заявку на участие</button>
              </form>
            </div>
          )}

        </div>
      </div>
    </div>
  );
}

export default Profile;