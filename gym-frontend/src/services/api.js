const API_BASE = 'http://localhost:8000';

const authHeaders = () => ({
  'Content-Type': 'application/json',
  'Authorization': `Bearer ${localStorage.getItem('access')}`,
});

const fetchWithRefresh = async (url, options) => {
  let r = await fetch(url, options);

  if (r.status === 401) {
    const refreshed = await refreshToken();  // usa fetch direto internamente
    if (refreshed) {
      options.headers['Authorization'] = `Bearer ${localStorage.getItem('access')}`;
      r = await fetch(url, options);  // ← fetch direto também, não fetchWithRefresh
    } else {
      logout();
      window.location.reload();  // redireciona pro login
      return r;  // ← importante: para a execução aqui
    }
  }

  return r;
};

export const loginUser = async (username, password) => {
  const r = await fetchWithRefresh(`${API_BASE}/gym/login/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  });
  return { ok: r.ok, data: await r.json() };
};

export const registerUser = async (username, email, phone_number, password) => {
  const r = await fetchWithRefresh(`${API_BASE}/gym/create-user/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, email, phone_number, password }),
  });
  return { ok: r.ok, data: await r.json() };
};

export const getProfile = async () => {
  const r = await fetchWithRefresh(`${API_BASE}/gym/user/`, {
    method: 'GET',
    headers: authHeaders(),
  });
  return { ok: r.ok, data: await r.json() };
};

export const updateProfile = async (username, email, phone_number) => {
  const r = await fetchWithRefresh(`${API_BASE}/gym/user/`, {
    method: 'PATCH',
    headers: authHeaders(),
    body: JSON.stringify({ username, email, phone_number }),
  });
  return { ok: r.ok, data: await r.json() };
};

export const createPayment = async (plan) => {
  const r = await fetchWithRefresh(`${API_BASE}/gym/plan-payment/`, {
    method: 'POST',
    headers: authHeaders(),
    body: JSON.stringify({ plan }),
  });
  return { httpStatus: r.status, data: await r.json() };
};

export const getPaymentStatus = async () => {
  const r = await fetchWithRefresh(`${API_BASE}/gym/payments/status/`, {
    method: 'get',
    headers: authHeaders(),
  });
  return { ok: r.ok, data: await r.json()};
};

export const confirmPayment = async (status, planId, paymentId) => {
  const r = await fetchWithRefresh(`${API_BASE}/gym/payments/confirm/`, {
    method: 'POST',
    headers: authHeaders(),
    body: JSON.stringify({ status, plan_id: planId, payment_id: paymentId }),
  });
  return { httpStatus: r.status, data: await r.json() };
};

export const cancelPlan = async () => {
  const r = await fetchWithRefresh(`${API_BASE}/gym/plan/cancel/`, {
    method: 'POST',
    headers: authHeaders(),
  });
  return { ok: r.ok, data: await r.json() };
};

export const refreshToken = async () => {
  const r = await fetch(`${API_BASE}/gym/refresh/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh: localStorage.getItem('refresh') }),
  });
  if (r.ok) {
    const data = await r.json();
    localStorage.setItem('access', data.access);
    return true;
  }
  return false;
};

export const logout = () => {
  localStorage.removeItem('access');
  localStorage.removeItem('refresh');
};
