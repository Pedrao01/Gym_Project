import { useState } from 'react';
import { loginUser } from '../services/api';
import { jwtDecode } from 'jwt-decode';

export default function Login({ onSwitchToRegister, onLogin }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [msg, setMsg] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleLogin = async () => {
    if (!username || !password) {
      setMsg({ type: 'error', text: 'Preencha todos os campos.' });
      return;
    }
    setLoading(true);
    setMsg(null);
    try {
      const { ok, data } = await loginUser(username, password);
      if (ok) {
        localStorage.setItem('access', data.access);
        localStorage.setItem('refresh', data.refresh);

        const decodedToken = jwtDecode(data.access);

        // is_staff vem no token decodificado — o Django pode incluir no payload
        // Por ora, detectamos pelo campo is_staff que o DRF pode retornar
        const isAdmin = decodedToken.is_staff === true;

        console.log('isAdmin:', data.is_staff)

        setMsg({ type: 'success', text: 'Login realizado com sucesso!' });
        setTimeout(() => onLogin(isAdmin), 800);
      } else {
        setMsg({ type: 'error', text: data.detail || 'Credenciais inválidas.' });
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
        <p className="text-sm text-gray-500 mt-1">Entre na sua conta</p>
      </div>

      {msg && (
        <div className={`text-sm px-3 py-2 rounded-lg mb-4 ${
          msg.type === 'error' ? 'bg-red-50 text-red-600' : 'bg-green-50 text-green-700'
        }`}>
          {msg.text}
        </div>
      )}

      <div className="mb-4">
        <label className="block text-xs font-medium text-gray-400 uppercase tracking-widest mb-1">Usuário</label>
        <input
          type="text"
          value={username}
          onChange={e => setUsername(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && handleLogin()}
          placeholder="seu_usuario"
          className="w-full px-4 py-2.5 text-sm border border-gray-200 rounded-lg outline-none focus:border-orange-500 focus:ring-2 focus:ring-orange-100"
        />
      </div>

      <div className="mb-4">
        <label className="block text-xs font-medium text-gray-400 uppercase tracking-widest mb-1">Senha</label>
        <input
          type="password"
          value={password}
          onChange={e => setPassword(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && handleLogin()}
          placeholder="••••••••"
          className="w-full px-4 py-2.5 text-sm border border-gray-200 rounded-lg outline-none focus:border-orange-500 focus:ring-2 focus:ring-orange-100"
        />
      </div>

      <button
        onClick={handleLogin}
        disabled={loading}
        className="w-full py-3 font-bebas text-xl tracking-widest text-white bg-orange-600 rounded-lg hover:bg-orange-700 disabled:opacity-50 transition-colors mt-1"
      >
        {loading ? 'AGUARDE...' : 'ENTRAR'}
      </button>

      <div className="flex items-center gap-3 my-4">
        <hr className="flex-1 border-gray-200" />
        <span className="text-xs text-gray-400 uppercase tracking-wider">ou</span>
        <hr className="flex-1 border-gray-200" />
      </div>

      <p className="text-center text-sm text-gray-400">
        Não tem conta?{' '}
        <span
          onClick={onSwitchToRegister}
          className="text-orange-600 font-medium cursor-pointer hover:underline"
        >
          Criar conta
        </span>
      </p>
    </div>
  );
}
