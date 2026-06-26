import React, { useState } from 'react';
import Header from './components/Layout/Header';
import Sidebar from './components/Layout/Sidebar';
import Home from './components/Pages/Home';
import About from './components/Pages/About';
import Program from './components/Pages/Program';
import Location from './components/Pages/Location';
import Contacts from './components/Pages/Contacts';
import Profile from './components/Pages/Profile';
import Admin from './components/Pages/Admin';
import './styles/App.css';

function App() {
  const [currentPage, setCurrentPage] = useState('home');
  const [isAdmin, setIsAdmin] = useState(false);

  const renderPage = () => {
    switch(currentPage) {
      case 'home': return <Home />;
      case 'about': return <About />;
      case 'program': return <Program />;
      case 'location': return <Location />;
      case 'contacts': return <Contacts />;
      case 'profile': return <Profile />;
      case 'admin': return <Admin />;
      default: return <Home />;
    }
  };

  return (
    <div className="app">
      <Header onNavigate={setCurrentPage} currentPage={currentPage} />
      <div className="app-body">
        {currentPage === 'admin' ? (
          <div className="admin-layout">
            <Sidebar onNavigate={setCurrentPage} currentPage={currentPage} />
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