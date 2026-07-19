import { useState, useEffect } from 'react';
import { listUsers, getAdminStats, toggleUserActive } from '../services/api';

const PLAN_LABEL = { mensal: 'Mensal', trimestral: 'Trimestral', anual: 'Anual' };

export default function AdminUsuarios() {
  const [users, setUsers] = useState([]);
  const [stats, setStats] = useState(null);
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [msg, setMsg] = useState(null);

  const fetchStats = async () => {
    const { ok, data } = await getAdminStats();
    if (ok) setStats(data);
  };

  const fetchUsers = async (p = 1, s = '') => {
    setLoading(true);
    const { ok, data } = await listUsers(p, s);
    if (ok) {
      setUsers(data.results || []);
      setTotal(data.count || 0);
      setTotalPages(Math.ceil((data.count || 0) / 10));
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchStats();
    fetchUsers(1, '');
  }, []);

  const handleSearch = () => {
    setPage(1);
    fetchUsers(1, search);
  };

  const handleClear = () => {
    setSearch('');
    setPage(1);
    fetchUsers(1, '');
  };

  const handlePage = (p) => {
    setPage(p);
    fetchUsers(p, search);
  };

  const handleToggle = async (user) => {
    const newStatus = !user.plan.is_active;

    const { ok } = await toggleUserActive(user.id, !user.plan.is_active);
    if (ok) {
      setUsers(prev =>
        prev.map(u => u.id === user.id
         ? { ...u, plan: { ...u.plan, is_active: newStatus } }
         : u
        )
      );
      fetchStats()

      setMsg({ type: 'success', text: `Usuário ${user.username} ${!user.plan.is_active ? 'ativado' : 'desativado'}.` });
      setTimeout(() => setMsg(null), 2500);
    } else {
      setMsg({ type: 'error', text: 'Erro ao atualizar usuário.' });
      setTimeout(() => setMsg(null), 2500);
    }
  };

  return (
    <div>
      <h1 className="font-bebas text-3xl tracking-widest text-gray-800 mb-5">Usuários</h1>

      {/* Contadores */}
      {stats && (
        <div className="grid grid-cols-3 gap-3 mb-5">
          <div className="bg-white border border-gray-100 rounded-2xl p-4">
            <p className="font-bebas text-4xl tracking-wide text-orange-600">{stats.total}</p>
            <p className="text-xs font-medium text-gray-400 uppercase tracking-widest mt-1">Total de usuários</p>
          </div>
          <div className="bg-white border border-gray-100 rounded-2xl p-4">
            <p className="font-bebas text-4xl tracking-wide text-green-700">{stats.with_plan}</p>
            <p className="text-xs font-medium text-gray-400 uppercase tracking-widest mt-1">Com plano ativo</p>
          </div>
          <div className="bg-white border border-gray-100 rounded-2xl p-4">
            <p className="font-bebas text-4xl tracking-wide text-red-700">{stats.without_plan}</p>
            <p className="text-xs font-medium text-gray-400 uppercase tracking-widest mt-1">Sem plano ativo</p>
          </div>
        </div>
      )}

      {/* Mensagem de feedback */}
      {msg && (
        <div className={`text-sm px-3 py-2 rounded-lg mb-4 ${
          msg.type === 'success' ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-600'
        }`}>
          {msg.text}
        </div>
      )}

      {/* Busca */}
      <div className="flex gap-2 mb-4">
        <input
          type="text"
          value={search}
          onChange={e => setSearch(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && handleSearch()}
          placeholder="Buscar por username..."
          className="flex-1 px-4 py-2.5 text-sm bg-white border border-gray-200 rounded-lg outline-none focus:border-orange-500 focus:ring-2 focus:ring-orange-100"
        />
        <button
          onClick={handleSearch}
          className="px-5 py-2.5 font-bebas text-lg tracking-widest text-white bg-orange-600 rounded-lg hover:bg-orange-700 transition-colors"
        >
          Buscar
        </button>
        <button
          onClick={handleClear}
          className="px-5 py-2.5 font-bebas text-lg tracking-widest text-gray-500 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
        >
          Limpar
        </button>
      </div>

      {/* Tabela */}
      <div className="bg-white border border-gray-100 rounded-2xl overflow-hidden mb-3">
        <table className="w-full border-collapse">
          <thead>
            <tr className="bg-gray-50 border-b border-gray-100">
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-widest">Usuário</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-widest">E-mail</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-widest">Telefone</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-widest">Plano</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-widest">Status</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-widest">Ação</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={6} className="px-4 py-8 text-center text-sm text-gray-400">
                  Carregando...
                </td>
              </tr>
            ) : users.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-4 py-8 text-center text-sm text-gray-400">
                  Nenhum usuário encontrado.
                </td>
              </tr>
            ) : users.map(user => (
              <tr key={user.id} className="border-b border-gray-50 hover:bg-gray-50 transition-colors last:border-0">
                <td className="px-4 py-3 text-sm font-medium text-gray-800">{user.username}</td>
                <td className="px-4 py-3 text-sm text-gray-500">{user.email}</td>
                <td className="px-4 py-3 text-sm text-gray-600">{user.phone_number}</td>
                <td className="px-4 py-3">
                  {user.plan ? (
                    <span className="text-xs font-medium px-2.5 py-1 rounded-full bg-blue-50 text-blue-700">
                      {PLAN_LABEL[user.plan.kind_plan] || user.plan.kindplan}
                    </span>
                  ) : (
                    <span className="text-xs font-medium px-2.5 py-1 rounded-full bg-gray-100 text-gray-500">
                      Sem plano
                    </span>
                  )}
                </td>
                <td className="px-4 py-3">
                  <span className={`text-xs font-medium px-2.5 py-1 rounded-full ${
                    user.plan.is_active
                      ? 'bg-green-50 text-green-700'
                      : 'bg-red-50 text-red-600'
                  }`}>
                    {user.plan.is_active ? '● Ativo' : '● Inativo'}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <button
                    onClick={() => handleToggle(user)}
                    className={`text-xs px-3 py-1.5 rounded-lg border transition-colors ${
                      user.plan.is_active
                        ? 'text-red-600 bg-red-50 border-red-200 hover:bg-red-100'
                        : 'text-green-700 bg-green-50 border-green-200 hover:bg-green-100'
                    }`}
                  >
                    {user.plan.is_active ? 'Desativar' : 'Ativar'}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Paginação */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between bg-white border border-gray-100 rounded-2xl px-4 py-3">
          <p className="text-xs text-gray-400">
            {total} usuário{total !== 1 ? 's' : ''} encontrado{total !== 1 ? 's' : ''}
          </p>
          <div className="flex gap-1.5">
            <button
              onClick={() => handlePage(page - 1)}
              disabled={page === 1}
              className="px-3 py-1.5 text-xs border border-gray-200 rounded-lg disabled:opacity-40 hover:border-orange-400 hover:text-orange-600 transition-colors"
            >
              ←
            </button>
            {Array.from({ length: totalPages }, (_, i) => i + 1).map(p => (
              <button
                key={p}
                onClick={() => handlePage(p)}
                className={`px-3 py-1.5 text-xs border rounded-lg transition-colors ${
                  p === page
                    ? 'bg-orange-600 text-white border-orange-600'
                    : 'border-gray-200 hover:border-orange-400 hover:text-orange-600'
                }`}
              >
                {p}
              </button>
            ))}
            <button
              onClick={() => handlePage(page + 1)}
              disabled={page === totalPages}
              className="px-3 py-1.5 text-xs border border-gray-200 rounded-lg disabled:opacity-40 hover:border-orange-400 hover:text-orange-600 transition-colors"
            >
              →
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
