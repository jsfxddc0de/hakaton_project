import React, { useState } from 'react';
import { programData } from '../../data/mockData';

function Program() {
  const [audioPlaying, setAudioPlaying] = useState(null);

  const handlePlayAudio = (id) => {
    setAudioPlaying(audioPlaying === id ? null : id);
  };

  return (
    <div className="program-container page-program">
      <h1 className="program-title"><span>✦ Программа ✦</span></h1>
      <div className="event-name">
        <span className="icon">💃</span>
        Танцевальный бал
      </div>
      <div className="event-info">
        <div className="info-item">
          <span className="icon">📅</span>
          <span>Дата: <span className="value">28 июня 2026</span></span>
        </div>
        <div className="info-item">
          <span className="icon">🕐</span>
          <span>Время: <span className="value">18:00 - 23:00</span></span>
        </div>
      </div>

      <div className="schedule">
        {programData.map((item, index) => (
          <React.Fragment key={item.id}>
            {item.divider && <div className="section-divider">✦ ✦ ✦</div>}
            <div className={`schedule-item ${item.featured ? 'featured-track-item' : ''}`}>
              <div className="schedule-time">
                <div className="time">{item.time}</div>
                <div className="duration">{item.duration}</div>
              </div>
              <div className="schedule-icon">{item.icon}</div>
              <div className="schedule-content">
                <div className="title-event" style={item.featured ? { color: '#f5d061' } : {}}>
                  {item.title}
                </div>
                <div className="description">{item.desc}</div>
                {item.audio && (
                  <div className="audio-player-wrapper">
                    <audio controls>
                      <source src={item.audio} type="audio/mpeg" />
                      Ваш браузер не поддерживает аудиоплеер.
                    </audio>
                  </div>
                )}
              </div>
            </div>
          </React.Fragment>
        ))}
      </div>

      <a href="#" className="btn-back" onClick={(e) => { e.preventDefault(); window.history.back(); }}>
        <span className="arrow">←</span> Назад к мероприятиям
      </a>
    </div>
  );
}

export default Program;