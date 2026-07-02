import { useState } from 'react';
import { registerUser } from '../services/api';

export default function Register({ onSwitchToLogin }) {
  const [form, setForm] = useState({ username: '', email: '', phone_number: '', password: '' });
  const [msg, setMsg] = useState(null);
  const [loading, setLoading] = useState(false);

  const set = (field) => (e) => setForm({ ...form, [field]: e.target.value });

  const handleRegister = async () => {
    const { username, email, phone_number, password } = form;
    if (!username || !email || !phone_number || !password) {
      setMsg({ type: 'error', text: 'Preencha todos os campos.' });
      return;
    }
    if (password.length < 8) {
      setMsg({ type: 'error', text: 'Senha deve ter no mínimo 8 caracteres.' });
      return;
    }
    setLoading(true);
    setMsg(null);
    try {
      const { ok, data } = await registerUser(username, email, phone_number, password);
      if (ok) {
        setMsg({ type: 'success', text: 'Conta criada com sucesso! Redirecionando...' });
        setTimeout(onSwitchToLogin, 1800);
      } else {
        const errs = data.errors;
        const text = typeof errs === 'string'
          ? errs
          : Object.entries(errs).map(([k, v]) => `${k}: ${Array.isArray(v) ? v[0] : v}`).join(' | ');
        setMsg({ type: 'error', text });
      }
    } catch {
      setMsg({ type: 'error', text: 'Erro de conexão. Verifique se o Django está rodando.' });
    }
    setLoading(false);
  };

  return (
    <div>
      <div className="text-center mb-8">
        <h1 className="font-bebas text-5xl tracking-widest text-orange-600">GYM</h1>
        <p className="text-sm text-gray-500 mt-1">Crie sua conta</p>
      </div>

      <p className="text-xs text-gray-400 bg-gray-50 border-l-4 border-orange-500 px-3 py-2 rounded-r mb-4">
        Endpoint: <code className="text-orange-500">POST /gym/user/</code>
      </p>

      {msg && (
        <div className={`text-sm px-3 py-2 rounded mb-4 ${
          msg.type === 'error' ? 'bg-red-50 text-red-600' : 'bg-green-50 text-green-600'
        }`}>
          {msg.text}
        </div>
      )}

      <div className="grid grid-cols-2 gap-3 mb-4">
        <div>
          <label className="block text-xs font-medium text-gray-400 uppercase tracking-widest mb-1">Usuário</label>
          <input
            type="text"
            value={form.username}
            onChange={set('username')}
            placeholder="joao_silva"
            className="w-full px-4 py-2.5 text-sm border border-gray-200 rounded-lg outline-none focus:border-orange-500 focus:ring-2 focus:ring-orange-100"
          />
        </div>
        <div>
          <label className="block text-xs font-medium text-gray-400 uppercase tracking-widest mb-1">Telefone</label>
          <input
            type="text"
            value={form.phone_number}
            onChange={set('phone_number')}
            placeholder="11999999999"
            maxLength={11}
            className="w-full px-4 py-2.5 text-sm border border-gray-200 rounded-lg outline-none focus:border-orange-500 focus:ring-2 focus:ring-orange-100"
          />
        </div>
      </div>

      <div className="mb-4">
        <label className="block text-xs font-medium text-gray-400 uppercase tracking-widest mb-1">E-mail</label>
        <input
          type="email"
          value={form.email}
          onChange={set('email')}
          placeholder="joao@email.com"
          className="w-full px-4 py-2.5 text-sm border border-gray-200 rounded-lg outline-none focus:border-orange-500 focus:ring-2 focus:ring-orange-100"
        />
      </div>

      <div className="mb-4">
        <label className="block text-xs font-medium text-gray-400 uppercase tracking-widest mb-1">Senha (mínimo 8 caracteres)</label>
        <input
          type="password"
          value={form.password}
          onChange={set('password')}
          placeholder="••••••••"
          className="w-full px-4 py-2.5 text-sm border border-gray-200 rounded-lg outline-none focus:border-orange-500 focus:ring-2 focus:ring-orange-100"
        />
      </div>

      <button
        onClick={handleRegister}
        disabled={loading}
        className="w-full py-3 font-bebas text-xl tracking-widest text-white bg-orange-600 rounded-lg hover:bg-orange-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors mt-1"
      >
        {loading ? 'AGUARDE...' : 'CRIAR CONTA'}
      </button>

      <div className="flex items-center gap-3 my-4">
        <hr className="flex-1 border-gray-200" />
        <span className="text-xs text-gray-400 uppercase tracking-wider">ou</span>
        <hr className="flex-1 border-gray-200" />
      </div>

      <p className="text-center text-sm text-gray-400">
        Já tem conta?{' '}
        <span
          onClick={onSwitchToLogin}
          className="text-orange-600 font-medium cursor-pointer hover:underline"
        >
          Fazer login
        </span>
      </p>
    </div>
  );
}
