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
        {programData.map((item, index) => {
          if (item.divider) {
            return <div key={`divider-${index}`} className="section-divider">✦ ✦ ✦</div>;
          }
          return (
            <div key={item.id} className={`schedule-item ${item.featured ? 'featured-track-item' : ''}`}>
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
          );
        })}
      </div>

      <div className="container" style={{ marginTop: '70px', paddingBottom: '70px' }}>
        <div style={{
          background: 'rgba(255, 255, 255, 0.02)',
          border: '1px solid rgba(212, 175, 55, 0.15)',
          borderRadius: '16px',
          padding: '40px'
        }}>
          <h2 className="modern-title" style={{ textAlign: 'center', marginBottom: '15px', fontSize: '2rem' }}>
            🗳️ Голосование за главный вальс бала
          </h2>
          <p style={{ color: '#a0aec0', fontSize: '0.95rem', textAlign: 'center', marginBottom: '35px' }}>
            Отдайте свой голос за композицию, которая завершит наш вечер! (Доступно только подтвержденным участникам)
          </p>

          <SongsVoteBlock />
        </div>
      </div>

      <a href="#" className="btn-back" onClick={(e) => { e.preventDefault(); window.history.back(); }}>
        <span className="arrow">←</span> Назад к мероприятиям
      </a>
    </div>
  );
}

// Sub-component for interactive song list voting
function SongsVoteBlock() {
  const [songs, setSongs] = React.useState([]);
  const [totalVotes, setTotalVotes] = React.useState(0);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState(null);

  const loadSongs = async () => {
    try {
      const data = await songsApi.getSongs();
      setSongs(data.songs || []);
      setTotalVotes(data.total_votes || 0);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  React.useEffect(() => {
    loadSongs();
  }, []);

  const handleVote = async (songId) => {
    try {
      await songsApi.vote(songId);
      alert('Ваш голос успешно учтен!');
      loadSongs();
    } catch (err) {
      alert('Ошибка при голосовании: ' + err.message);
    }
  };

  if (loading) return <div style={{ color: '#dfb743', textAlign: 'center' }}>Загрузка плейлиста...</div>;
  if (error) return <div style={{ color: '#f56565', textAlign: 'center' }}>Войдите в личный кабинет, чтобы принять участие в голосовании.</div>;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {songs.map((song) => (
        <div key={song.id} style={{
          background: song.is_current ? 'rgba(212, 175, 55, 0.04)' : 'rgba(0, 0, 0, 0.2)',
          border: song.is_current ? '1px solid #dfb743' : '1px solid rgba(255, 255, 255, 0.05)',
          borderRadius: '12px',
          padding: '24px',
          display: 'grid',
          gridTemplateColumns: '1fr 2fr 1fr',
          alignItems: 'center',
          gap: '20px'
        }}>
          <div>
            <h4 style={{ color: '#fff', fontSize: '1.1rem', marginBottom: '5px', fontWeight: 'bold' }}>{song.title}</h4>
            <p style={{ color: '#a0aec0', fontSize: '0.85rem' }}>{song.desc}</p>
          </div>
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', color: '#a0aec0', marginBottom: '8px' }}>
              <span>Прогресс голосов ({song.votes})</span>
              <span style={{ color: '#dfb743', fontWeight: 'bold' }}>{song.percent}%</span>
            </div>
            <div style={{ width: '100%', height: '8px', background: 'rgba(255,255,255,0.05)', borderRadius: '4px', overflow: 'hidden' }}>
              <div style={{ width: `${song.percent}%`, height: '100%', background: 'linear-gradient(90deg, #dfb743, #fff0a5)', borderRadius: '4px', transition: 'width 0.5s ease-out' }}></div>
            </div>
          </div>
          <div style={{ textAlign: 'right' }}>
            {song.is_current ? (
              <span style={{ color: '#dfb743', fontWeight: 'bold', fontSize: '0.9rem', display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: '5px' }}>
                ✓ Ваш голос
              </span>
            ) : (
              <button className="action ok" onClick={() => handleVote(song.id)} style={{ padding: '8px 16px', fontSize: '0.85rem' }}>
                Проголосовать
              </button>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}

// Make songsApi accessible in the component scope
import { songsApi } from '../../data/api';

export default Program;