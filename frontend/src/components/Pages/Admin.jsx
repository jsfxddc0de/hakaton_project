import React, { useState, useEffect } from 'react';
import { adminApi } from '../../data/api';

function Admin() {
  const [searchTerm, setSearchTerm] = useState('');
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);

  const loadDashboard = async () => {
    try {
      const data = await adminApi.getDashboard();
      setRequests(data.requests || []);
    } catch (e) {
      alert('Ошибка загрузки дашборда: ' + e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboard();
  }, []);

  const handleApprove = async (id) => {
    try {
      await adminApi.approve(id);
      loadDashboard();
    } catch (err) {
      alert('Ошибка при одобрении заявки: ' + err.message);
    }
  };

  const handleReject = async (id) => {
    try {
      await adminApi.reject(id);
      loadDashboard();
    } catch (err) {
      alert('Ошибка при отклонении заявки: ' + err.message);
    }
  };

  const handleExport = () => {
    // Open backend excel download route in new window
    window.open('http://localhost:8000/admin/export/excel', '_blank');
  };

  const getStatusClass = (status) => {
    const map = {
      'Новая': 'new',
      'Подтверждена': 'ok',
      'Отклонена': 'reject'
    };
    return map[status] || '';
  };

  const dynamicStats = [
    { value: requests.length, label: 'Всего заявок' },
    { value: requests.filter(r => r.status === 'Подтверждена').length, label: 'Подтверждено' },
    { value: requests.filter(r => r.status === 'Новая').length, label: 'Новых' },
    { value: requests.filter(r => r.status === 'Отклонена').length, label: 'Отклонено' }
  ];

  const filteredRequests = requests.filter((req) =>
    (req.name && req.name.toLowerCase().includes(searchTerm.toLowerCase())) ||
    (req.id && req.id.toLowerCase().includes(searchTerm.toLowerCase())) ||
    (req.email && req.email.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh', color: '#dfb743', fontWeight: 'bold' }}>
        Загрузка панели администратора...
      </div>
    );
  }

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
        {dynamicStats.map((stat, index) => (
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
              <th>Действия</th>
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
                  {req.status === 'Новая' ? (
                    <div style={{ display: 'flex', gap: '8px' }}>
                      <button 
                        onClick={() => handleApprove(req.id)}
                        style={{
                          backgroundColor: 'rgba(0, 255, 140, 0.12)',
                          color: '#65ffb5',
                          border: '1px solid rgba(0, 255, 140, 0.3)',
                          padding: '6px 12px',
                          borderRadius: '8px',
                          cursor: 'pointer',
                          fontSize: '0.8rem',
                          fontWeight: 'bold',
                          transition: 'all 0.2s'
                        }}
                        title="Одобрить заявку"
                      >
                        ✓
                      </button>
                      <button 
                        onClick={() => handleReject(req.id)}
                        style={{
                          backgroundColor: 'rgba(255, 90, 90, 0.12)',
                          color: '#ff9d9d',
                          border: '1px solid rgba(255, 90, 90, 0.3)',
                          padding: '6px 12px',
                          borderRadius: '8px',
                          cursor: 'pointer',
                          fontSize: '0.8rem',
                          fontWeight: 'bold',
                          transition: 'all 0.2s'
                        }}
                        title="Отклонить заявку"
                      >
                        ✗
                      </button>
                    </div>
                  ) : (
                    <span style={{ color: '#8e99b8', fontSize: '0.85rem' }}>Решено</span>
                  )}
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