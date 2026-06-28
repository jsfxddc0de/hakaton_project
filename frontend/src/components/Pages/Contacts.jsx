import React from 'react';
import { contactsData } from '../../data/mockData';

function Contacts() {
  return (
    <section className="contacts-cyber-section" id="contacts">
      <div className="ambient-glow-1"></div>
      <div className="ambient-glow-2"></div>
      <div className="cyber-container">
        <div className="cyber-sticky-panel">
          <div className="cyber-badge">Связь 24/7</div>
          <h2 className="cyber-title">
            Команда <br />управления <br />
            <span className="gold-neon-text">бала</span>
          </h2>
          <p className="cyber-desc">
            Возникли вопросы по дресс-коду, билетам или координации? Мы создали эту цепочку быстрого реагирования, чтобы помочь вам в любую секунду.
          </p>
          <div className="cyber-line-decor"></div>
        </div>

        <div className="cyber-timeline">
          {contactsData.map((contact) => (
            <div 
              key={contact.id} 
              className={`timeline-item ${contact.isMain ? 'main-leader' : ''} ${contact.isHelpers ? 'helpers-special-item' : ''}`}
            >
              <div className="timeline-node">{contact.icon}</div>
              <div className={`timeline-content-card ${contact.isHelpers ? 'helpers-card' : ''}`}>
                {!contact.isHelpers ? (
                  <>
                    <div className="card-top">
                      <span className={`role-tag ${contact.isMain ? 'gold-border' : 'silver-border'}`}>
                        {contact.role}
                      </span>
                      <div className="status-indicator">
                        <span className="pulse-ring"></span>В сети
                      </div>
                    </div>
                    <h3 className="member-name">{contact.name}</h3>
                    <a href={`tel:${contact.phone}`} className="member-phone">{contact.phone}</a>
                    <p className="member-info">{contact.desc}</p>
                  </>
                ) : (
                  <>
                    <h4 className="helpers-title-modern">{contact.title}</h4>
                    <p className="helpers-desc-modern">{contact.desc}</p>
                    <div className="cyber-tags-container">
                      {contact.helpers?.map((helper) => (
                        <div key={helper} className="cyber-tag-pill">
                          <span className="pill-icon">🙋‍♂️</span>
                          <span className="pill-name">{helper}</span>
                        </div>
                      ))}
                    </div>
                  </>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="container" style={{ marginTop: '70px', paddingBottom: '70px', maxWidth: '600px' }}>
        <div style={{
          background: 'rgba(255, 255, 255, 0.02)',
          border: '1px solid rgba(255, 255, 255, 0.05)',
          borderRadius: '16px',
          padding: '40px',
          boxShadow: '0 15px 35px rgba(0, 0, 0, 0.2)'
        }}>
          <h3 style={{ color: '#dfb743', marginBottom: '15px', textAlign: 'center', fontSize: '1.6rem' }}>Остались вопросы?</h3>
          <p style={{ color: '#a0aec0', fontSize: '0.9rem', textAlign: 'center', marginBottom: '25px' }}>
            Напишите нам, и линейный координатор свяжется с вами в течение 10 минут.
          </p>
          <form onSubmit={(e) => { e.preventDefault(); alert('Ваше сообщение успешно отправлено оргкомитету!'); e.target.reset(); }} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            <div className="input-group">
              <label htmlFor="contact-name">Как к вам обращаться</label>
              <input type="text" id="contact-name" required className="form-input" placeholder="Введите имя" />
            </div>
            <div className="input-group">
              <label htmlFor="contact-email">Ваш контактный Email</label>
              <input type="email" id="contact-email" required className="form-input" placeholder="example@mail.ru" />
            </div>
            <div className="input-group">
              <label htmlFor="contact-msg">Сообщение или вопрос</label>
              <textarea id="contact-msg" required rows={4} className="form-input" placeholder="Задайте ваш вопрос..." style={{ resize: 'vertical' }} />
            </div>
            <button type="submit" className="btn-submit" style={{ width: '100%' }}>Отправить сообщение</button>
          </form>
        </div>
      </div>
    </section>
  );
}

export default Contacts;