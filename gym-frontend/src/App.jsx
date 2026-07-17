import { useState } from 'react';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './Dashboard';
import AdminDashboard from './AdminDashboard';

const params = new URLSearchParams(window.location.search);
const paymentStatus = params.get('status');

export default function App() {
  const [tab, setTab] = useState('login');
  const [isLoggedIn, setIsLoggedIn] = useState(!!localStorage.getItem('access'));
  const [isAdmin, setIsAdmin] = useState(!!localStorage.getItem('isAdmin'));

  const handleLogin = (admin = false) => {
    if (admin) localStorage.setItem('is_admin', 'true');
    setIsAdmin(admin);
    setIsLoggedIn(true);
  };

  if (isLoggedIn) {
    return isAdmin
      ? <AdminDashboard />
      : <Dashboard paymentStatus={paymentStatus} />;
  }

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="w-full max-w-md bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">

        <div className="flex border-b border-gray-100">
          <button
            onClick={() => setTab('login')}
            className={`flex-1 py-4 text-xs font-medium uppercase tracking-widest transition-colors border-b-2 ${
              tab === 'login'
                ? 'text-orange-600 border-orange-600'
                : 'text-gray-400 border-transparent hover:text-gray-600'
            }`}
          >
            Login
          </button>
          <button
            onClick={() => setTab('register')}
            className={`flex-1 py-4 text-xs font-medium uppercase tracking-widest transition-colors border-b-2 ${
              tab === 'register'
                ? 'text-orange-600 border-orange-600'
                : 'text-gray-400 border-transparent hover:text-gray-600'
            }`}
          >
            Cadastro
          </button>
        </div>

        <div className="p-8">
          {tab === 'login'
            ? <Login onSwitchToRegister={() => setTab('register')} onLogin={handleLogin} />
            : <Register onSwitchToLogin={() => setTab('login')} />
          }
        </div>

      </div>
    </div>
  );
}
