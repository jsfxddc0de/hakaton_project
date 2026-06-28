import React from 'react';

function Sidebar({ onNavigate, currentPage, onLogout }) {
  return (
    <div className="sidebar">
      <div className="sidebar-title">ADMIN PANEL</div>
      <ul className="menu-list">
        <li className={`menu-item with-arrow ${currentPage === 'admin' ? 'active' : ''}`}>
          <a href="#" onClick={(e) => { e.preventDefault(); onNavigate('admin'); }}>
            Заявки
          </a>
        </li>
        <li className="menu-item">
          <a href="#" onClick={(e) => { e.preventDefault(); alert("Раздел 'Пользователи' в разработке"); }}>
            Пользователи
          </a>
        </li>
        <li className="menu-item">
          <a href="#" onClick={(e) => { e.preventDefault(); alert("Раздел 'Настройки' в разработке"); }}>
            Настройки
          </a>
        </li>
      </ul>
      <div className="sidebar-footer" style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
        <a href="#" className="btn-action" style={{ textAlign: 'center', background: 'rgba(255,255,255,0.05)', color: '#fff', border: '1px solid rgba(255,255,255,0.1)', display: 'block', padding: '10px', borderRadius: '8px', textDecoration: 'none' }} onClick={(e) => { e.preventDefault(); onNavigate('home'); }}>
          На главную
        </a>
        <a href="#" className="btn-action btn-logout" style={{ textAlign: 'center', display: 'block', padding: '10px', borderRadius: '8px', textDecoration: 'none' }} onClick={(e) => { e.preventDefault(); onLogout(); }}>
          Выйти
        </a>
      </div>
    </div>
  );
}

export default Sidebar;