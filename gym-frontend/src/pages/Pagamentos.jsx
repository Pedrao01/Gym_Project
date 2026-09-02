import { useState, useEffect } from 'react';
import { getPaymentStatus, createPayment, cancelPlan, confirmPayment} from '../services/api';

const PLANS = [
  { id: 'mensal', name: 'Mensal', price: 'R$50', period: '/mês', features: 'Acesso completo · Sem fidelidade' },
  { id: 'trimestral', name: 'Trimestral', price: 'R$120', period: '/3 meses', features: 'Acesso completo · Economia de R$48' },
  { id: 'anual', name: 'Anual', price: 'R$899', period: '/ano', features: 'Acesso completo · Economia de R$289' },
];

export default function Pagamentos() {
  const [selectedPlan, setSelectedPlan] = useState('mensal');
  const [status, setStatus] = useState(null);
  const [msg, setMsg] = useState(null);
  const [loading, setLoading] = useState(false);
  const [confirmed, setConfirmed] = useState(false);

  useEffect(() => {
  const init = async () => {
    setLoading(true);

    const params = new URLSearchParams(window.location.search); // lê da URL real
    const paymentStatus = params.get('status');

    // 1. Verifica se já tem plano ativo
    const { ok, data: currentStatus } = await getPaymentStatus();
    if (ok && currentStatus) {
      setStatus(currentStatus); // já tem plano, só exibe
      setLoading(false);
      if (currentStatus.is_valid) {
        return;
      }
    }
    // 2. Se não tem plano ativo, verifica se veio um pagamento da URL
    if (!paymentStatus || confirmed) {
      setLoading(false);
      return;
    }

    setConfirmed(true);

    // 3. Confirma o pagamento com o backend
//     const plan = PLANS.find(p => p.id === selectedPlan);
    const planId = localStorage.getItem('selectedPlan') || selectedPlan
    const plan = PLANS.find(p => p.id === planId)
    localStorage.removeItem('selectedPlan')
    const paymentId = params.get('payment_id');
    const status = params.get('status')

    if (status === 'approved') {
        const { httpStatus, data } = await confirmPayment(paymentId);

        if (httpStatus === 200) {
          setMsg({ type: 'success', text: '✅ Pagamento aprovado! Seu plano já está ativo.' });
          setStatus(data);
        } else if (httpStatus === 202) {
          setMsg({ type: 'warning', text: '⏳ Pagamento pendente. Aguarde a confirmação.' });
        } else if (httpStatus === 400) {
          setMsg({ type: 'error', text: '❌ Pagamento recusado. Tente novamente.' });
        }
    }
    setMsg({ type: 'error', text: '❌ Falha em efetuar o pagamento. Tente novamente.'})

    // 4. Limpa a URL independente do resultado
    window.history.replaceState({}, '', '/');
    setLoading(false);
  };

  init();
}, []); // roda na montagem (paymentStatus vem da URL, já está disponível)

  const handleCheckout = async () => {
    setLoading(true);
    setMsg(null);
    const plan = PLANS.find(p => p.id === selectedPlan)
    localStorage.setItem('selectedPlan', plan.id)
    const { httpStatus, data } = await createPayment(plan.id);
    if (httpStatus === 200 && data.init_point) {
      window.location.href = data.init_point;
    } else {
      setMsg({ type: 'error', text: data?.error || 'Erro ao criar pagamento. Tente novamente.' });
    }
    setLoading(false);
  };

  const handleCancel = async () => {
    if (!confirm('Tem certeza que deseja cancelar seu plano?')) return;
    const { ok, data } = await cancelPlan();
    if (ok) {
      setStatus({
        plan_name: data.plan_name,
        status: 'cancelled',
        expires_at: data.expires_at
      });
      setMsg({ type: 'success', text: '✅ Plano cancelado com sucesso.' });
    } else {
      setMsg({ type: 'error', text: '❌ Erro ao cancelar plano.' });
    }
  };

  const statusColor = {
    approved: 'bg-green-50 text-green-700',
    pending: 'bg-amber-50 text-amber-700',
    cancelled: 'bg-red-50 text-red-600',
  };

  const statusLabel = {
    approved: 'Ativo',
    pending: 'Pendente',
    cancelled: 'Cancelado',
  };

  return (
    <div>
      <h1 className="font-bebas text-3xl tracking-widest text-gray-800 mb-5">Pagamentos</h1>

      {msg && (
        <div className={`text-sm px-3 py-2 rounded-lg mb-4 max-w-lg ${
              msg.type === 'success' ? 'bg-green-50 text-green-700'
              : msg.type === 'warning' ? 'bg-amber-50 text-amber-700'
              : 'bg-red-50 text-red-600'
            }`}>
          {msg.text}
        </div>
      )}

      {status ? (
        <div className="bg-white border border-gray-100 rounded-2xl p-5 max-w-lg mb-4">
          <p className="text-xs font-medium text-gray-400 uppercase tracking-widest mb-3">Plano atual</p>
          <div className="flex items-center justify-between flex-wrap gap-3">
            <div>
              <p className="font-medium text-gray-800">{status.plan_name || 'Plano ativo'}</p>
              {status.expires_at && (
                <p className="text-xs text-gray-400 mt-1">
                  Vencimento: <span className="font-medium text-gray-600">{status.expires_at}</span>
                </p>
              )}
            </div>
            <div className="flex items-center gap-3">
              <span className={`text-xs font-medium px-3 py-1 rounded-full ${
                status.is_active ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-600'
              }`}>
                {status.is_active ? 'Ativo' : 'Cancelado'}
              </span>

              {status.is_active && (
                <button
                  onClick={handleCancel}
                  className="text-sm px-3 py-1.5 text-red-600 bg-red-50 border border-red-200 rounded-lg hover:bg-red-100 transition-colors"
                >
                  Cancelar plano
                </button>
              )}
            </div>
          </div>
        </div>
      ) : (
        <div className="bg-gray-50 border border-gray-100 rounded-2xl p-5 max-w-lg mb-4">
          <p className="text-sm text-gray-500">Você ainda não tem um plano ativo.</p>
        </div>
      )}

      <div className="bg-white border border-gray-100 rounded-2xl p-5 max-w-lg">
        <p className="text-xs font-medium text-gray-400 uppercase tracking-widest mb-4">Assinar novo plano</p>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-5">
          {PLANS.map((plan) => (
            <div
              key={plan.id}
              onClick={() => setSelectedPlan(plan.id)}
              className={`rounded-xl p-3 cursor-pointer transition-all border ${
                selectedPlan === plan.id
                  ? 'border-orange-500 border-2'
                  : 'border-gray-100 hover:border-orange-300'
              }`}
            >
              <p className="font-medium text-sm text-gray-800 mb-1">{plan.name}</p>
              <p className="font-bebas text-2xl tracking-wide text-orange-600">{plan.price}</p>
              <p className="text-xs text-gray-400">{plan.period}</p>
              <p className="text-xs text-gray-400 mt-2 leading-relaxed">{plan.features}</p>
            </div>
          ))}
        </div>

        <div className="flex items-center justify-between flex-wrap gap-3">
          <div className="flex items-center gap-2 text-xs text-gray-400 bg-gray-50 border border-gray-100 rounded-lg px-3 py-2">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
            </svg>
            Pagamento via Mercado Pago
          </div>
          <button
            onClick={handleCheckout}
            disabled={loading}
            className="py-2.5 px-6 font-bebas text-lg tracking-widest text-white bg-orange-600 rounded-lg hover:bg-orange-700 disabled:opacity-50 transition-colors"
          >
            {loading ? 'Aguarde...' : 'Pagar agora'}
          </button>
        </div>
      </div>
    </div>
  );
}
