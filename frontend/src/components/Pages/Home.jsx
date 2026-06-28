import React from 'react';
import Countdown from '../Common/Countdown';

function Home() {
  return (
    <section className="hero page-home">
      <div className="hero-bg"></div>
      <div className="container">
        <div className="hero-content">
          <div className="hero-subtitle-top">Школьный</div>
          <h1 className="hero-title gold-gradient">Танцевальный<br />Бал</h1>
          <div className="hero-descr-title">Вечер грации, музыки и волшебства</div>
          <p className="hero-text">
            Погрузитесь в атмосферу классического бала:<br />
            танцы, музыка, новые знакомства<br />
            и незабываемые впечатления!
          </p>
          <Countdown targetDate={new Date(2026, 5, 28, 18, 0, 0)} />
        </div>
      </div>

      <section className="about-section">
        <div className="container">
          <h2 className="section-title">О мероприятии</h2>
          <div className="grid-info">
            <div className="info-card">
              <h3><i className="fa-regular fa-star"></i> О мероприятии</h3>
              <p>Танцевальный бал – это традиционное школьное мероприятие, объединяющее элегантность, культуру и творчество.</p>
            </div>
            <div className="info-card">
              <h3><i className="fa-solid fa-bullseye"></i> Цели</h3>
              <p>Развитие музыкальной культуры, навыков общения и создание незабываемых воспоминаний.</p>
            </div>
            <div className="info-card">
              <h3><i className="fa-solid fa-users"></i> Ключевые факты</h3>
              <ul>
                <li>Ежегодное событие</li>
                <li>Участие более 200 учеников</li>
                <li>Живая музыка и мастер-классы</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      <section className="dress-code-section" style={{ padding: '60px 0', borderTop: '1px solid rgba(255,255,255,0.05)' }}>
        <div className="container">
          <h2 className="section-title" style={{ textAlign: 'center', marginBottom: '40px' }}>Дресс-код мероприятия</h2>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '30px' }}>
            <div className="info-card" style={{ padding: '30px' }}>
              <h3 style={{ color: '#dfb743', marginBottom: '15px', display: 'flex', alignItems: 'center', gap: '10px' }}>
                🤵 Джентльменам
              </h3>
              <p style={{ color: '#a0aec0', fontSize: '0.95rem', lineHeight: '1.6' }}>
                Обязателен классический смокинг или строгий темный костюм (черный, темно-синий). Белая классическая рубашка, галстук-бабочка и начищенные туфли. Маска для участия в маскараде приветствуется.
              </p>
            </div>
            <div className="info-card" style={{ padding: '30px' }}>
              <h3 style={{ color: '#dfb743', marginBottom: '15px', display: 'flex', alignItems: 'center', gap: '10px' }}>
                👗 Дамам
              </h3>
              <p style={{ color: '#a0aec0', fontSize: '0.95rem', lineHeight: '1.6' }}>
                Вечернее или бальное платье в пол. Рекомендуется пастельная или глубокая темная цветовая гамма. Классическая вечерняя прическа и удобная танцевальная обувь на устойчивом каблуке.
              </p>
            </div>
          </div>
        </div>
      </section>

      <section className="steps-section" style={{ padding: '60px 0', background: 'rgba(255,255,255,0.01)', borderTop: '1px solid rgba(255,255,255,0.05)' }}>
        <div className="container">
          <h2 className="section-title" style={{ textAlign: 'center', marginBottom: '40px' }}>Как попасть на бал</h2>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '30px' }}>
            <div className="info-card" style={{ padding: '30px', textAlign: 'center' }}>
              <div style={{ fontSize: '2.5rem', color: '#dfb743', marginBottom: '15px', fontWeight: 'bold' }}>1</div>
              <h3 style={{ marginBottom: '10px' }}>Регистрация</h3>
              <p style={{ color: '#a0aec0', fontSize: '0.9rem' }}>
                Создайте аккаунт и подайте заявку на участие в личном кабинете, указав пожелания.
              </p>
            </div>
            <div className="info-card" style={{ padding: '30px', textAlign: 'center' }}>
              <div style={{ fontSize: '2.5rem', color: '#dfb743', marginBottom: '15px', fontWeight: 'bold' }}>2</div>
              <h3 style={{ marginBottom: '10px' }}>Подтверждение</h3>
              <p style={{ color: '#a0aec0', fontSize: '0.9rem' }}>
                Модераторы оргкомитета проверят данные и одобрят вашу кандидатуру.
              </p>
            </div>
            <div className="info-card" style={{ padding: '30px', textAlign: 'center' }}>
              <div style={{ fontSize: '2.5rem', color: '#dfb743', marginBottom: '15px', fontWeight: 'bold' }}>3</div>
              <h3 style={{ marginBottom: '10px' }}>Танцы!</h3>
              <p style={{ color: '#a0aec0', fontSize: '0.9rem' }}>
                Получите пригласительный билет, готовьте костюм и приходите в Колонный зал!
              </p>
            </div>
          </div>
        </div>
      </section>
    </section>
  );
}

export default Home;