import React from 'react';

function Sidebar({ onNavigate, currentPage }) {
  return (
    <div className="sidebar">
      <div className="sidebar-title">Личный кабинет</div>
      <ul className="menu-list">
        <li className="menu-item with-arrow">
          <a href="#" onClick={() => onNavigate('admin')}>
            Заявки
          </a>
        </li>
        <li className="menu-item with-arrow">
          <a href="#">Избранное</a>
        </li>
        <li className="menu-item">
          <a href="#">Мои организации</a>
        </li>
      </ul>
      <div className="sidebar-footer">
        <a href="#" className="btn-action btn-logout">Выйти из аккаунта</a>
        <a href="#" className="btn-action btn-delete">Удалить профиль</a>
      </div>
    </div>
  );
}

export default Sidebar;