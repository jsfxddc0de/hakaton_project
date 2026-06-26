import React from 'react';

function About() {
  const features = [
    { number: '01', title: 'Свет и звук', desc: 'Профессиональное световое шоу, лазерные эффекты и мощный звук, которые полностью заполнят всё пространство зала.' },
    { number: '02', title: 'Дресс-код: Сияй', desc: 'Изысканные костюмы и вечерние платья под неоновыми софитами. Идеальный момент, чтобы показать свой стиль.', featured: true },
    { number: '03', title: 'Атмосфера', desc: 'Сотни горящих глаз, новые знакомства, танцевальные баттлы и кульминация вечера — выбор Короля и Королевы бала.' },
    { number: '04', title: 'Медиацентр', desc: 'Интерактивные фотозоны, работа топовых фотографов и крутые видеоролики — твой контент разорвет соцсети.' }
  ];

  return (
    <section className="about-modern-section" id="about">
      <div className="decor-blur-1"></div>
      <div className="decor-blur-2"></div>
      <div className="modern-container">
        <div className="modern-intro">
          <span className="modern-subtitle">Главное событие года</span>
          <h2 className="modern-title">
            Энергия танца. <br />
            <span className="gold-gradient">Магия момента.</span>
          </h2>
          <p className="modern-text">
            Школьный Танцевальный Бал полностью стирает границы между классической эстетикой и современным драйвом.
            Это не просто вечер — это масштабное шоу, где классические традиции переплетаются с клубной атмосферой,
            а каждый трек заставляет сердце биться чаще.
          </p>
          <p className="modern-text-highlight">
            Готовь свой лучший образ: этот вечер разделит твою школьную жизнь на «до» и «после».
          </p>
        </div>
        <div className="modern-grid">
          {features.map((item) => (
            <div 
              key={item.number} 
              className={`modern-card glass-effect ${item.featured ? 'featured-card' : ''}`}
            >
              <div className="card-number">{item.number}</div>
              <div className="card-content">
                <h3>{item.title}</h3>
                <p>{item.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

export default About;