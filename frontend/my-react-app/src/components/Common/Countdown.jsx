import React, { useState, useEffect } from 'react';

function Countdown({ targetDate }) {
  const [timeLeft, setTimeLeft] = useState({
    days: 0,
    hours: 0,
    minutes: 0,
    seconds: 0
  });

  useEffect(() => {
    const timer = setInterval(() => {
      const now = new Date().getTime();
      const distance = targetDate.getTime() - now;

      if (distance < 0) {
        clearInterval(timer);
        return;
      }

      setTimeLeft({
        days: Math.floor(distance / (1000 * 60 * 60 * 24)),
        hours: Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60)),
        minutes: Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60)),
        seconds: Math.floor((distance % (1000 * 60)) / 1000)
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [targetDate]);

  const format = (num) => String(num).padStart(2, '0');

  return (
    <div className="countdown-box">
      <div className="countdown-title">До начала бала осталось:</div>
      <div className="countdown-timer">
        <div className="timer-item">
          <span className="number">{format(timeLeft.days)}</span>
          <span className="label">дней</span>
        </div>
        <div className="timer-item">
          <span className="number">{format(timeLeft.hours)}</span>
          <span className="label">часов</span>
        </div>
        <div className="timer-item">
          <span className="number">{format(timeLeft.minutes)}</span>
          <span className="label">минут</span>
        </div>
        <div className="timer-item">
          <span className="number">{format(timeLeft.seconds)}</span>
          <span className="label">секунд</span>
        </div>
      </div>
    </div>
  );
}

export default Countdown;