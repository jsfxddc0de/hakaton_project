const API_BASE = 'http://localhost:8000/api';

async function request(path, options = {}) {
  const url = `${API_BASE}${path}`;
  const defaultOptions = {
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };
  
  const response = await fetch(url, defaultOptions);
  
  if (!response.ok) {
    let errorMsg = 'Что-то пошло не так';
    try {
      const data = await response.json();
      errorMsg = data.error || errorMsg;
    } catch (e) {}
    throw new Error(errorMsg);
  }
  
  if (response.status === 204) return null;
  return response.json();
}

export const authApi = {
  me: () => request('/auth/me'),
  login: (email, password) => request('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  }),
  register: (data) => request('/auth/register', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  verify: (code) => request('/auth/verify', {
    method: 'POST',
    body: JSON.stringify({ code }),
  }),
  logout: () => request('/auth/logout', { method: 'POST' }),
};

export const songsApi = {
  getSongs: () => request('/songs'),
  vote: (songId) => request(`/songs/vote/${songId}`, { method: 'POST' }),
};

export const profileApi = {
  getProfile: () => request('/profile'),
  update: (phone) => request('/profile/update', {
    method: 'POST',
    body: JSON.stringify({ phone }),
  }),
  apply: (eventId, wishes) => request('/profile/apply', {
    method: 'POST',
    body: JSON.stringify({ event_id: eventId, wishes }),
  }),
};

export const adminApi = {
  getDashboard: () => request('/admin/dashboard'),
  approve: (appId) => request(`/admin/approve/${encodeURIComponent(appId)}`, { method: 'POST' }),
  reject: (appId) => request(`/admin/reject/${encodeURIComponent(appId)}`, { method: 'POST' }),
};
