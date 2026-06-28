import React, { useState, useEffect } from 'react';
import Header from './components/Layout/Header';
import Sidebar from './components/Layout/Sidebar';
import Home from './components/Pages/Home';
import About from './components/Pages/About';
import Program from './components/Pages/Program';
import Location from './components/Pages/Location';
import Contacts from './components/Pages/Contacts';
import Profile from './components/Pages/Profile';
import Admin from './components/Pages/Admin';
import Login from './components/Pages/Login';
import Register from './components/Pages/Register';
import Verify from './components/Pages/Verify';
import { authApi } from './data/api';
import './styles/App.css';

function App() {
  const [currentPage, setCurrentPage] = useState('home');
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const u = await authApi.me();
        setUser(u);
      } catch (e) {
        setUser(null);
      } finally {
        setLoading(false);
      }
    };
    checkAuth();
  }, []);

  const handleLoginSuccess = (u) => {
    setUser(u);
    setCurrentPage(u.role === 'admins' ? 'admin' : 'profile');
  };

  const handleLogout = async () => {
    try {
      await authApi.logout();
      setUser(null);
      setCurrentPage('home');
    } catch (e) {
      alert('Ошибка при выходе из системы');
    }
  };

  const renderPage = () => {
    if (loading) {
      return (
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '80vh', color: '#dfb743', fontWeight: 'bold' }}>
          Загрузка...
        </div>
      );
    }

    switch(currentPage) {
      case 'home': return <Home />;
      case 'about': return <About />;
      case 'program': return <Program />;
      case 'location': return <Location />;
      case 'contacts': return <Contacts />;
      case 'login': return <Login onLoginSuccess={handleLoginSuccess} onNavigate={setCurrentPage} />;
      case 'register': return <Register onNavigate={setCurrentPage} />;
      case 'verify': return <Verify onLoginSuccess={handleLoginSuccess} onNavigate={setCurrentPage} />;
      case 'profile': 
        return user ? <Profile user={user} onLogout={handleLogout} /> : <Login onLoginSuccess={handleLoginSuccess} onNavigate={setCurrentPage} />;
      case 'admin': 
        return user && user.role === 'admins' ? <Admin onLogout={handleLogout} /> : <Home />;
      default: return <Home />;
    }
  };

  return (
    <div className="app">
      <Header onNavigate={setCurrentPage} currentPage={currentPage} user={user} onLogout={handleLogout} />
      <div className="app-body">
        {currentPage === 'admin' ? (
          <div className="admin-layout">
            <Sidebar onNavigate={setCurrentPage} currentPage={currentPage} onLogout={handleLogout} />
            <main className="admin-content">
              {renderPage()}
            </main>
          </div>
        ) : (
          <main className="main-content">
            {renderPage()}
          </main>
        )}
      </div>
    </div>
  );
}

export default App;