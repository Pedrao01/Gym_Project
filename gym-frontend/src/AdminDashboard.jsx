import { useState, useEffect } from 'react';
import AdminUsuarios from './pages/AdminUsuarios';
import { logout, getProfile } from './services/api';

const NAV = [
  { id: 'usuarios', label: 'Usuários', icon: '👥' },
];

export default function AdminDashboard() {
  const [page, setPage] = useState('usuarios');
  const [admin, setAdmin] = useState(null);

  useEffect(() => {
    getProfile().then(({ ok, data }) => {
      if (ok) setAdmin(data);
    });
  }, []);

  const handleLogout = () => {
    logout();
    window.location.reload();
  };

  const initials = admin?.username?.slice(0, 2).toUpperCase() || 'AD';

  return (
    <div className="min-h-screen bg-gray-50 flex">
      <aside className="w-56 bg-white border-r border-gray-100 flex flex-col flex-shrink-0">

        {/* Logo */}
        <div className="px-5 py-5 border-b border-gray-100">
          <span className="font-bebas text-3xl tracking-widest text-orange-600">GYM</span>
          <p className="text-xs font-medium text-gray-400 uppercase tracking-widest mt-0.5">Painel Admin</p>
        </div>

        {/* Card do admin */}
        <div className="m-3 bg-gray-50 border border-gray-100 rounded-xl p-3">
          <div className="w-10 h-10 rounded-full bg-orange-50 flex items-center justify-center text-orange-700 font-medium text-sm mb-2">
            {initials}
          </div>
          <p className="font-medium text-sm text-gray-800 truncate">{admin?.username || '...'}</p>
          <p className="text-xs text-orange-600 font-medium uppercase tracking-wide mt-0.5">Administrador</p>
          {admin?.email && (
            <p className="text-xs text-gray-400 mt-2 truncate">{admin.email}</p>
          )}
        </div>

        {/* Navegação */}
        <nav className="flex-1 py-2">
          {NAV.map(item => (
            <button
              key={item.id}
              onClick={() => setPage(item.id)}
              className={`w-full flex items-center gap-3 px-5 py-2.5 text-sm text-left transition-all border-l-2 ${
                page === item.id
                  ? 'text-orange-600 bg-orange-50 border-orange-600'
                  : 'text-gray-500 border-transparent hover:bg-gray-50 hover:text-gray-700'
              }`}
            >
              <span>{item.icon}</span>
              {item.label}
            </button>
          ))}
        </nav>

        {/* Logout */}
        <div className="px-3 py-3 border-t border-gray-100">
          <button
            onClick={handleLogout}
            className="w-full flex items-center justify-center gap-2 py-2 text-xs text-gray-400 border border-gray-200 rounded-lg hover:bg-red-50 hover:text-red-600 hover:border-red-200 transition-colors"
          >
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4M16 17l5-5-5-5M21 12H9"/>
            </svg>
            Sair
          </button>
        </div>
      </aside>

      <main className="flex-1 p-8 min-w-0">
        {page === 'usuarios' && <AdminUsuarios />}
      </main>
    </div>
  );
}
