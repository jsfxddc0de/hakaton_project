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
    </section>
  );
}

export default Location;