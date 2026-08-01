import { useState, useEffect } from 'react';
import { getProfile, updateProfile } from '../services/api';

export default function Perfil() {
  const [form, setForm] = useState({ username: '', email: '', phone_number: '' });
  const [msg, setMsg] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    getProfile().then(({ ok, data }) => {
      if (ok) setForm({ username: data.username, email: data.email, phone_number: data.phone_number });
    });
  }, []);

  const set = (field) => (e) => setForm({ ...form, [field]: e.target.value });

  const save = async () => {
    setLoading(true);
    setMsg(null);
    const { ok } = await updateProfile(form.username, form.email, form.phone_number);
    setMsg(ok
      ? { type: 'success', text: 'Perfil atualizado com sucesso!' }
      : { type: 'error', text: 'Erro ao atualizar perfil. Esse(s) valor(es) já está/estão em uso.' }
    );
    setLoading(false);
  };

  const initials = form.username.slice(0, 2).toUpperCase() || '??';

  return (
    <div>
      <h1 className="font-bebas text-3xl tracking-widest text-gray-800 mb-5">Meu perfil</h1>

      <div className="bg-white border border-gray-100 rounded-2xl p-6 max-w-lg">
        <div className="flex items-center gap-4 mb-6">
          <div className="w-12 h-12 rounded-full bg-orange-50 flex items-center justify-center text-orange-700 font-medium text-sm">
            {initials}
          </div>
          <div>
            <p className="font-medium text-gray-800">{form.username || 'Aluno'}</p>
            <p className="text-xs text-gray-400">Aluno ativo</p>
          </div>
        </div>

        {msg && (
          <div className={`text-sm px-3 py-2 rounded-lg mb-4 ${
            msg.type === 'success' ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-600'
          }`}>
            {msg.text}
          </div>
        )}

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-3">
          <div>
            <label className="block text-xs font-medium text-gray-400 uppercase tracking-widest mb-1">Usuário</label>
            <input
              type="text"
              value={form.username}
              onChange={set('username')}
              className="w-full px-3 py-2 text-sm bg-gray-50 border border-gray-200 rounded-lg outline-none focus:border-orange-500 focus:ring-2 focus:ring-orange-100"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-400 uppercase tracking-widest mb-1">Telefone</label>
            <input
              type="text"
              value={form.phone_number}
              onChange={set('phone_number')}
              maxLength={11}
              className="w-full px-3 py-2 text-sm bg-gray-50 border border-gray-200 rounded-lg outline-none focus:border-orange-500 focus:ring-2 focus:ring-orange-100"
            />
          </div>
        </div>

        <div className="mb-4">
          <label className="block text-xs font-medium text-gray-400 uppercase tracking-widest mb-1">E-mail</label>
          <input
            type="email"
            value={form.email}
            onChange={set('email')}
            className="w-full px-3 py-2 text-sm bg-gray-50 border border-gray-200 rounded-lg outline-none focus:border-orange-500 focus:ring-2 focus:ring-orange-100"
          />
        </div>

        <button
          onClick={save}
          disabled={loading}
          className="py-2.5 px-6 font-bebas text-lg tracking-widest text-white bg-orange-600 rounded-lg hover:bg-orange-700 disabled:opacity-50 transition-colors"
        >
          {loading ? 'Salvando...' : 'Salvar'}
        </button>
      </div>
    </div>
  );
}
