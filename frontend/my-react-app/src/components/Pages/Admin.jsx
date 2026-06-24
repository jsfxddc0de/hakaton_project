import React, { useState } from 'react';
import { adminStats, adminRequests } from '../../data/mockData';

function Admin() {
  const [searchTerm, setSearchTerm] = useState('');
  const [requests, setRequests] = useState(adminRequests);

  const filteredRequests = requests.filter((req) =>
    req.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    req.id.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleExport = () => {
    alert('Экспорт в Excel (mock)');
  };

  const handleEdit = (id) => {
    alert(`Редактирование заявки ${id}`);
  };

  const getStatusClass = (status) => {
    const map = {
      'Новая': 'new',
      'Подтверждена': 'ok',
      'Отклонена': 'reject'
    };
    return map[status] || '';
  };

  return (
    <div className="admin-dashboard page-admin">
      <div className="hero">
        <div>
          <div className="badge">Административная панель</div>
          <h1>Управление заявками</h1>
          <p>Контроль и обработка пользовательских заявок</p>
        </div>
        <button className="export-btn" onClick={handleExport}>
          Выгрузить Excel
        </button>
      </div>

      <div className="stats">
        {adminStats.map((stat, index) => (
          <div className="stat" key={index}>
            <h2>{stat.value}</h2>
            <span>{stat.label}</span>
          </div>
        ))}
      </div>

      <div className="table-card">
        <div className="table-header">
          <h3>Последние заявки</h3>
          <input
            className="search"
            placeholder="Поиск заявки..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>ФИО</th>
              <th>Класс</th>
              <th>Email</th>
              <th>Статус</th>
              <th>Дата</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {filteredRequests.map((req) => (
              <tr key={req.id}>
                <td>{req.id}</td>
                <td>{req.name}</td>
                <td>{req.class}</td>
                <td>{req.email}</td>
                <td>
                  <span className={`status ${getStatusClass(req.status)}`}>
                    {req.status}
                  </span>
                </td>
                <td>{req.date}</td>
                <td>
                  <button className="action" onClick={() => handleEdit(req.id)}>
                    <i className="fa-solid fa-pen"></i>
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default Admin;