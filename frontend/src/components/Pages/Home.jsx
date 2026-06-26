import React from 'react';
import Countdown from '../Common/Countdown';

function Home() {
  return (
    <section className="hero page-home">
      <div className="hero-bg"></div>
      <div className="container">
        <div className="hero-content">
          <div className="hero-subtitle-top">Школьный</div>
          <h1 className="gold-gradient">Танцевальный<br />Бал</h1>
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
    </section>
  );
}

export default Home;