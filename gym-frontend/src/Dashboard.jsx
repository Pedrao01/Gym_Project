import { useState, useEffect } from 'react';
import Perfil from './pages/Perfil';
import Pagamentos from './pages/Pagamentos';
import { logout } from './services/api';

const NAV = [
  { id: 'perfil', label: 'Meu perfil', icon: '👤' },
  { id: 'pagamentos', label: 'Pagamentos', icon: '💳' },
];

export default function Dashboard({ paymentStatus }) {
  const [page, setPage] = useState(paymentStatus ? 'pagamentos' : 'perfil');
  const [collapsed, setCollapsed] = useState(window.innerWidth < 768);

  useEffect(() => {
    const handleResize = () => setCollapsed(window.innerWidth < 768);
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const handleLogout = () => {
    logout();
    window.location.reload();
  };

  return (
    <div className="min-h-screen bg-gray-50 flex">
      <aside
        className={`bg-white border-r border-gray-100 flex flex-col transition-all duration-200 ${
          collapsed ? 'w-16' : 'w-52'
        }`}
      >
        <div className="px-5 py-5 border-b border-gray-100 flex items-center justify-between">
          {!collapsed && (
            <span className="font-bebas text-3xl tracking-widest text-orange-600">GYM</span>
          )}
          <button
            onClick={() => setCollapsed(!collapsed)}
            className="text-gray-400 hover:text-orange-600 transition-colors"
            title={collapsed ? 'Expandir menu' : 'Recolher menu'}
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              {collapsed
                ? <path d="M9 18l6-6-6-6" />   // seta pra direita (abrir)
                : <path d="M15 18l-6-6 6-6" /> // seta pra esquerda (fechar)
              }
            </svg>
          </button>
        </div>

        <nav className="flex-1 py-3">
          {NAV.map((item) => (
            <button
              key={item.id}
              onClick={() => setPage(item.id)}
              title={collapsed ? item.label : undefined}
              className={`w-full flex items-center gap-3 px-5 py-2.5 text-sm text-left transition-all border-l-2 ${
                collapsed ? 'justify-center px-0' : ''
              } ${
                page === item.id
                  ? 'text-orange-600 bg-orange-50 border-orange-600'
                  : 'text-gray-500 border-transparent hover:bg-gray-50 hover:text-gray-700'
              }`}
            >
              <span>{item.icon}</span>
              {!collapsed && item.label}
            </button>
          ))}
        </nav>

        <div className="px-4 py-4 border-t border-gray-100">
          <button
            onClick={handleLogout}
            title={collapsed ? 'Sair' : undefined}
            className="w-full flex items-center justify-center gap-2 py-2 text-xs text-gray-400 border border-gray-200 rounded-lg hover:bg-red-50 hover:text-red-600 hover:border-red-200 transition-colors"
          >
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4M16 17l5-5-5-5M21 12H9"/>
            </svg>
            {!collapsed && 'Sair'}
          </button>
        </div>
      </aside>

      <main className="flex-1 p-8">
        {page === 'perfil' && <Perfil />}
        {page === 'pagamentos' && <Pagamentos/>}
      </main>
    </div>
  );
}