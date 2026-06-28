import React from 'react';

function Location() {
  return (
    <section className="location-section" id="location">
      <div className="decor-blur-3"></div>
      <div className="location-container">
        <div className="location-info glass-effect">
          <span className="location-subtitle">Где всё произойдет</span>
          <h2 className="location-title">
            Локация <br />
            <span className="gold-gradient">и координаты</span>
          </h2>
          <div className="info-item">
            <div className="info-icon">📍</div>
            <div className="info-text">
              <h4>Адрес</h4>
              <p>г. Москва, улица Пушкина, дом Колотушкина</p>
            </div>
          </div>
          <div className="info-item">
            <div className="info-icon">🚗</div>
            <div className="info-text">
              <h4>Как добраться</h4>
              <p>Ближайшая станция метро находится в пешей доступности. Для гостей на машинах предусмотрена охраняемая парковка.</p>
            </div>
          </div>
          <div className="info-item">
            <div className="info-icon">🚪</div>
            <div className="info-text">
              <h4>Вход</h4>
              <p>Сбор гостей начинается за 45 минут до официального старта. Не забудьте показать ваш пригласительный билет на контроле.</p>
            </div>
          </div>
        </div>
        <div className="location-map-container glass-effect">
          <iframe
            className="google-map"
            src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d2250.776657920199!2d37.20845771583489!3d55.60960710811915!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x46b556db6c250621%3A0x3cb3b12dd3722022!2z0YPQuy4g0J_Rg9GI0LrQuNC90LAsINCc0L7RgdC60LLQsCwg0KDQvtGB0YHQQuNGPLCAxNDMzNTA!5e0!3m2!1sru!2sru!4v1718967000000!5m2!1sru!2sru"
            allowFullScreen=""
            loading="lazy"
            referrerPolicy="no-referrer-when-downgrade"
            title="Карта расположения"
          ></iframe>
        </div>
      </div>

      <div className="container" style={{ marginTop: '50px', paddingBottom: '50px' }}>
        <div style={{
          display: 'grid',
          gridTemplateColumns: '1.5fr 1fr',
          gap: '30px',
          background: 'rgba(255, 255, 255, 0.02)',
          border: '1px solid rgba(255, 255, 255, 0.05)',
          borderRadius: '16px',
          padding: '40px'
        }}>
          <div>
            <h3 style={{ color: '#dfb743', marginBottom: '20px', fontSize: '1.5rem' }}>Парковка и Логистика</h3>
            <p style={{ color: '#a0aec0', fontSize: '0.95rem', lineHeight: '1.7', marginBottom: '15px' }}>
              Для всех участников бала организован бесплатный охраняемый паркинг непосредственно у здания Колонного Зала. При въезде на территорию необходимо предъявить электронный билет или назвать свои ФИО сотруднику охраны.
            </p>
            <p style={{ color: '#a0aec0', fontSize: '0.95rem', lineHeight: '1.7' }}>
              От станций метро каждые 15 минут будут курсировать комфортабельные шаттлы с логотипом «Осенний Бал 2026». Проезд бесплатный по пригласительным билетам.
            </p>
          </div>
          <div style={{ borderLeft: '1px solid rgba(255, 255, 255, 0.08)', paddingLeft: '30px' }}>
            <h3 style={{ color: '#dfb743', marginBottom: '20px', fontSize: '1.5rem' }}>Что взять с собой</h3>
            <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <li style={{ display: 'flex', gap: '10px', fontSize: '0.95rem', color: '#a0aec0' }}>
                <span style={{ color: '#dfb743' }}>✓</span> Пригласительный QR-код (в телефоне или распечатанный)
              </li>
              <li style={{ display: 'flex', gap: '10px', fontSize: '0.95rem', color: '#a0aec0' }}>
                <span style={{ color: '#dfb743' }}>✓</span> Документ, удостоверяющий личность
              </li>
              <li style={{ display: 'flex', gap: '10px', fontSize: '0.95rem', color: '#a0aec0' }}>
                <span style={{ color: '#dfb743' }}>✓</span> Сменную танцевальную обувь (обязательное требование зала)
              </li>
              <li style={{ display: 'flex', gap: '10px', fontSize: '0.95rem', color: '#a0aec0' }}>
                <span style={{ color: '#dfb743' }}>✓</span> Праздничную маску для маскарада
              </li>
            </ul>
          </div>
        </div>
      </div>
    </section>
  );
}

export default Location;