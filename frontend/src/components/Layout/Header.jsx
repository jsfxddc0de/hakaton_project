import React from 'react';

function Header({ onNavigate, currentPage, user, onLogout }) {
  const navItems = [
    { id: 'home', label: 'Главная' },
    { id: 'about', label: 'О мероприятии' },
    { id: 'program', label: 'Программа' },
    { id: 'location', label: 'Место' },
    { id: 'contacts', label: 'Контакты' },
  ];

  if (user) {
    if (user.role === 'admins') {
      navItems.push({ id: 'admin', label: 'Админ-панель' });
    }
    navItems.push({ id: 'profile', label: 'Личный кабинет' });
  } else {
    navItems.push({ id: 'login', label: 'Войти' });
  }

  return (
    <header className="header">
      <div className="container nav-container">
        <div className="logo" style={{ cursor: 'pointer' }} onClick={() => onNavigate('home')}>
          <i className="fa-solid fa-person-dancing"></i>
          <span>Танцевальный Бал</span>
        </div>
        <ul className="nav-menu">
          {navItems.map((item) => (
            <li key={item.id}>
              <a
                href="#"
                className={currentPage === item.id ? 'active' : ''}
                onClick={(e) => {
                  e.preventDefault();
                  onNavigate(item.id);
                }}
              >
                {item.label}
              </a>
            </li>
          ))}
          {user && (
            <li>
              <button 
                onClick={onLogout}
                style={{
                  background: 'rgba(255, 90, 90, 0.1)',
                  border: '1px solid rgba(255, 90, 90, 0.3)',
                  color: '#ff9d9d',
                  padding: '6px 12px',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  fontSize: '0.8rem',
                  marginLeft: '10px'
                }}
              >
                Выйти
              </button>
            </li>
          )}
        </ul>
      </div>
    </header>
  );
}

export default Header;