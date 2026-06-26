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
    </section>
  );
}

export default Contacts;