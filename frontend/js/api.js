/**
 * api.js — Centralized API wrapper for Airline Web App
 * Handles JWT tokens, fetch, error processing.
 */

const API_BASE = 'http://localhost:8000/api/v1';

// ──────────────────────────────────────────
// Token management
// ──────────────────────────────────────────

const Auth = {
    getAccess: () => localStorage.getItem('access_token'),
    getRefresh: () => localStorage.getItem('refresh_token'),
    setTokens: (access, refresh) => {
        localStorage.setItem('access_token', access);
        if (refresh) localStorage.setItem('refresh_token', refresh);
    },
    clearTokens: () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user_info');
    },
    getUser: () => {
        try { return JSON.parse(localStorage.getItem('user_info')); }
        catch { return null; }
    },
    setUser: (user) => localStorage.setItem('user_info', JSON.stringify(user)),
    isLoggedIn: () => !!localStorage.getItem('access_token'),
    isAdmin: () => {
        const u = Auth.getUser();
        return u && u.role === 'admin';
    },
    isManager: () => {
        const u = Auth.getUser();
        return u && (u.role === 'admin' || u.role === 'manager');
    }
};

// ──────────────────────────────────────────
// Core fetch wrapper
// ──────────────────────────────────────────

async function apiFetch(path, options = {}) {
    const url = `${API_BASE}${path}`;
    const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };

    const token = Auth.getAccess();
    if (token) headers['Authorization'] = `Bearer ${token}`;

    let response = await fetch(url, { ...options, headers });

    // Token expired — attempt refresh
    if (response.status === 401 && Auth.getRefresh()) {
        const refreshed = await tryRefreshToken();
        if (refreshed) {
            headers['Authorization'] = `Bearer ${Auth.getAccess()}`;
            response = await fetch(url, { ...options, headers });
        } else {
            Auth.clearTokens();
            window.location.href = '/login.html';
            return;
        }
    }

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new ApiError(response.status, errorData);
    }

    // 204 No Content
    if (response.status === 204) return null;

    return response.json();
}

async function tryRefreshToken() {
    try {
        const res = await fetch(`${API_BASE}/auth/token/refresh/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh: Auth.getRefresh() })
        });
        if (!res.ok) return false;
        const data = await res.json();
        Auth.setTokens(data.access, data.refresh);
        return true;
    } catch {
        return false;
    }
}

class ApiError extends Error {
    constructor(status, data) {
        super(JSON.stringify(data));
        this.status = status;
        this.data = data;
    }

    getMessages() {
        const msgs = [];
        if (!this.data) return ['Unknown error occurred'];
        const traverse = (obj, prefix = '') => {
            for (const [k, v] of Object.entries(obj)) {
                if (Array.isArray(v)) msgs.push(...v.map(m => prefix ? `${prefix}: ${m}` : m));
                else if (typeof v === 'object' && v) traverse(v, k);
                else msgs.push(prefix ? `${prefix}: ${v}` : v);
            }
        };
        if (typeof this.data === 'object') traverse(this.data);
        else msgs.push(String(this.data));
        return msgs.length ? msgs : ['An error occurred.'];
    }
}

// ──────────────────────────────────────────
// API endpoints
// ──────────────────────────────────────────

const api = {
    // Auth
    auth: {
        login: (email, password) =>
            apiFetch('/auth/login/', { method: 'POST', body: JSON.stringify({ email, password }) }),
        register: (data) =>
            apiFetch('/auth/register/', { method: 'POST', body: JSON.stringify(data) }),
        logout: (refresh) =>
            apiFetch('/auth/logout/', { method: 'POST', body: JSON.stringify({ refresh }) }),
        profile: () => apiFetch('/auth/profile/'),
        passengerProfile: () => apiFetch('/auth/profile/passenger/'),
        changePassword: (data) =>
            apiFetch('/auth/profile/change-password/', { method: 'POST', body: JSON.stringify(data) }),
    },

    // Flights (public)
    flights: {
        list: (params = {}) => {
            const qs = new URLSearchParams(params).toString();
            return apiFetch(`/flights/${qs ? '?' + qs : ''}`);
        },
        get: (id) => apiFetch(`/flights/${id}/`),
        airports: (search = '') => apiFetch(`/flights/airports/${search ? '?search=' + search : ''}`),
    },

    // Admin flights
    adminFlights: {
        list: (params = {}) => {
            const qs = new URLSearchParams(params).toString();
            return apiFetch(`/flights/admin/${qs ? '?' + qs : ''}`);
        },
        create: (data) =>
            apiFetch('/flights/admin/', { method: 'POST', body: JSON.stringify(data) }),
        update: (id, data) =>
            apiFetch(`/flights/admin/${id}/`, { method: 'PATCH', body: JSON.stringify(data) }),
        delete: (id) =>
            apiFetch(`/flights/admin/${id}/`, { method: 'DELETE' }),
    },

    // Admin airports
    adminAirports: {
        list: () => apiFetch('/flights/admin/airports/'),
        create: (data) =>
            apiFetch('/flights/admin/airports/', { method: 'POST', body: JSON.stringify(data) }),
        update: (id, data) =>
            apiFetch(`/flights/admin/airports/${id}/`, { method: 'PATCH', body: JSON.stringify(data) }),
        delete: (id) =>
            apiFetch(`/flights/admin/airports/${id}/`, { method: 'DELETE' }),
    },

    // Admin aircraft
    adminAircraft: {
        list: () => apiFetch('/flights/admin/aircraft/'),
        create: (data) =>
            apiFetch('/flights/admin/aircraft/', { method: 'POST', body: JSON.stringify(data) }),
        update: (id, data) =>
            apiFetch(`/flights/admin/aircraft/${id}/`, { method: 'PATCH', body: JSON.stringify(data) }),
        delete: (id) =>
            apiFetch(`/flights/admin/aircraft/${id}/`, { method: 'DELETE' }),
    },

    // Bookings
    bookings: {
        create: (flightId, seatNumber) =>
            apiFetch('/bookings/', { method: 'POST', body: JSON.stringify({ flight_id: flightId, seat_number: seatNumber }) }),
        myBookings: () => apiFetch('/bookings/my/'),
        get: (id) => apiFetch(`/bookings/${id}/`),
        cancel: (id) =>
            apiFetch(`/bookings/${id}/cancel/`, { method: 'POST', body: JSON.stringify({}) }),
        myTickets: () => apiFetch('/bookings/tickets/'),
    },

    // Admin users
    adminUsers: {
        list: (params = {}) => {
            const qs = new URLSearchParams(params).toString();
            return apiFetch(`/auth/users/${qs ? '?' + qs : ''}`);
        },
        get: (id) => apiFetch(`/auth/users/${id}/`),
        update: (id, data) =>
            apiFetch(`/auth/users/${id}/`, { method: 'PATCH', body: JSON.stringify(data) }),
        delete: (id) =>
            apiFetch(`/auth/users/${id}/`, { method: 'DELETE' }),
    },
};

// ──────────────────────────────────────────
// UI helpers (shared across pages)
// ──────────────────────────────────────────

function showAlert(containerId, message, type = 'danger') {
    const el = document.getElementById(containerId);
    if (!el) return;
    el.innerHTML = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>`;
}

function showErrors(containerId, apiError) {
    const msgs = apiError instanceof ApiError ? apiError.getMessages() : [String(apiError)];
    showAlert(containerId, msgs.map(m => `<div>• ${m}</div>`).join(''), 'danger');
}

function formatDate(iso) {
    if (!iso) return '—';
    return new Date(iso).toLocaleString('ru-RU', {
        day: '2-digit', month: '2-digit', year: 'numeric',
        hour: '2-digit', minute: '2-digit'
    });
}

function formatPrice(price) {
    return Number(price).toLocaleString('ru-RU', { style: 'currency', currency: 'USD' });
}

function statusBadge(status) {
    const map = {
        scheduled: 'success', boarding: 'primary', departed: 'info',
        arrived: 'secondary', delayed: 'warning', cancelled: 'danger',
        active: 'success', used: 'secondary', pending: 'warning', confirmed: 'success'
    };
    return `<span class="badge bg-${map[status] || 'secondary'}">${status}</span>`;
}

function requireAuth(redirectTo = '/login.html') {
    if (!Auth.isLoggedIn()) {
        window.location.href = redirectTo;
        return false;
    }
    return true;
}

function requireAdmin() {
    if (!Auth.isLoggedIn() || !Auth.isManager()) {
        window.location.href = '/index.html';
        return false;
    }
    return true;
}

function updateNavbar() {
    const navAuth = document.getElementById('nav-auth');
    const navUser = document.getElementById('nav-user');
    const navAdmin = document.getElementById('nav-admin');
    if (!navAuth) return;

    if (Auth.isLoggedIn()) {
        const user = Auth.getUser();
        navAuth.classList.add('d-none');
        navUser.classList.remove('d-none');
        document.getElementById('nav-username').textContent = user?.username || 'User';
        if (Auth.isManager() && navAdmin) navAdmin.classList.remove('d-none');
    } else {
        navAuth.classList.remove('d-none');
        navUser.classList.add('d-none');
        if (navAdmin) navAdmin.classList.add('d-none');
    }
}