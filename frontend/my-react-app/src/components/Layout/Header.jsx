import React from 'react';

function Header({ onNavigate, currentPage }) {
  const navItems = [
    { id: 'home', label: 'Главная' },
    { id: 'about', label: 'О мероприятии' },
    { id: 'program', label: 'Программа' },
    { id: 'location', label: 'Место' },
    { id: 'contacts', label: 'Контакты' },
    { id: 'profile', label: 'Личный кабинет' },
    { id: 'admin', label: 'Админ-панель' },
  ];

  return (
    <header className="header">
      <div className="container nav-container">
        <div className="logo">
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
        </ul>
      </div>
    </header>
  );
}

export default Header;