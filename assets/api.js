/**
 * Nexus Tower - Unified API Client & Operations Data Layer
 * Handles authentication, HTTP error normalization, and real-time backend sync.
 */

(function (window) {
  'use strict';

  const API_BASE = '/api';

  class NexusAPIClient {
    constructor() {
      this.tokenKey = 'nexus-token';
      this.userKey = 'nexus-user';
      this.roleKey = 'nexus-role';
      this.rolePageKey = 'nexus-role-page';
    }

    getToken() {
      return (
        sessionStorage.getItem(this.tokenKey) ||
        localStorage.getItem(this.tokenKey) ||
        null
      );
    }

    setSession(token, user) {
      if (token) {
        sessionStorage.setItem(this.tokenKey, token);
        localStorage.setItem(this.tokenKey, token);
      }
      if (user) {
        const userJson = JSON.stringify(user);
        sessionStorage.setItem(this.userKey, userJson);
        localStorage.setItem(this.userKey, userJson);

        const role = user.role || 'procurement';
        const rolePageMap = {
          admin: 'controlTower',
          procurement: 'procurement',
          inventory: 'inventory',
          production: 'production',
          logistics: 'logistics',
        };
        const page = rolePageMap[role] || 'controlTower';

        sessionStorage.setItem(this.roleKey, role);
        localStorage.setItem(this.roleKey, role);
        sessionStorage.setItem(this.rolePageKey, page);
        localStorage.setItem(this.rolePageKey, page);
      }
    }

    clearSession() {
      sessionStorage.removeItem(this.tokenKey);
      sessionStorage.removeItem(this.userKey);
      sessionStorage.removeItem(this.roleKey);
      sessionStorage.removeItem(this.rolePageKey);

      localStorage.removeItem(this.tokenKey);
      localStorage.removeItem(this.userKey);
      localStorage.removeItem(this.roleKey);
      localStorage.removeItem(this.rolePageKey);
    }

    getCurrentUser() {
      try {
        const stored =
          sessionStorage.getItem(this.userKey) ||
          localStorage.getItem(this.userKey);
        if (stored) {
          return JSON.parse(stored);
        }
      } catch (e) {
        console.error('Error parsing stored user session:', e);
      }
      return null;
    }

    isAuthenticated() {
      return !!this.getToken();
    }

    async request(endpoint, options = {}) {
      const url = `${API_BASE}/${endpoint.replace(/^\//, '')}`;
      const headers = {
        Accept: 'application/json',
        ...(options.headers || {}),
      };

      const token = this.getToken();
      if (token && !headers['Authorization']) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      if (options.body && typeof options.body === 'object' && !(options.body instanceof FormData)) {
        headers['Content-Type'] = 'application/json';
        options.body = JSON.stringify(options.body);
      }

      try {
        const response = await fetch(url, {
          ...options,
          headers,
        });

        // Handle specific HTTP Status Codes cleanly
        if (response.status === 401) {
          console.warn('API Unauthorized (401) at:', endpoint);
          // If not currently on login page, redirect or notify
          const isLoginPage = window.location.pathname.endsWith('login.html') || window.location.pathname.endsWith('/login');
          if (!isLoginPage && !options.skipAuthRedirect) {
            this.clearSession();
            window.location.href = 'login.html?expired=true';
            throw new Error('Session expired. Please log in again.');
          }
        }

        let data = null;
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
          data = await response.json();
        } else {
          const text = await response.text();
          data = text ? { message: text } : {};
        }

        if (!response.ok) {
          const detailMsg =
            data?.detail ||
            data?.message ||
            `HTTP error ${response.status}: ${response.statusText}`;
          const err = new Error(detailMsg);
          err.status = response.status;
          err.data = data;
          throw err;
        }

        return data;
      } catch (error) {
        if (!error.status) {
          error.status = 0; // Network or proxy error
        }
        console.error(`API Request Failed [${options.method || 'GET'} ${endpoint}]:`, error);
        throw error;
      }
    }

    // ==================== AUTH METHODS ====================

    async login(email, password) {
      const data = await this.request('/auth/login', {
        method: 'POST',
        body: { email, password },
        skipAuthRedirect: true,
      });

      if (data && data.access_token) {
        this.setSession(data.access_token, data.user);
      }
      return data;
    }

    async logout() {
      try {
        await this.request('/auth/logout', { method: 'POST', skipAuthRedirect: true });
      } catch (e) {
        // Logout is best-effort on backend
      } finally {
        this.clearSession();
        window.location.href = 'login.html';
      }
    }

    async fetchCurrentUser() {
      try {
        const user = await this.request('/auth/me');
        if (user) {
          const storedToken = this.getToken();
          this.setSession(storedToken, user);
        }
        return user;
      } catch (e) {
        return this.getCurrentUser();
      }
    }

    // ==================== DOMAIN DATA METHODS ====================

    async getProducts() {
      return this.request('/products/');
    }

    async getSuppliers() {
      return this.request('/suppliers/');
    }

    async getInventory() {
      return this.request('/inventory/');
    }

    async getPurchaseOrders() {
      return this.request('/purchase-orders/');
    }

    async getPurchaseOrder(id) {
      return this.request(`/purchase-orders/${id}`);
    }

    async getProductionOrders() {
      return this.request('/production-orders/');
    }

    async getShipments() {
      return this.request('/shipments/');
    }

    async getAlerts(status = null) {
      const qs = status ? `?status=${encodeURIComponent(status)}` : '';
      return this.request(`/alerts/${qs}`);
    }

    async getRisks() {
      return this.request('/risks/');
    }

    async getRecommendations(status = null) {
      const qs = status ? `?status=${encodeURIComponent(status)}` : '';
      return this.request(`/recommendations/${qs}`);
    }

    async approveRecommendation(id) {
      return this.request(`/recommendations/${id}/approve`, {
        method: 'POST',
      });
    }

    async getEvents(limit = 100) {
      return this.request(`/events/?limit=${limit}`);
    }

    // ==================== UI HELPERS ====================

    showToast(message, type = 'success') {
      const existing = document.getElementById('nexus-toast');
      if (existing) existing.remove();

      const toast = document.createElement('div');
      toast.id = 'nexus-toast';
      toast.className = `fixed bottom-6 right-6 z-50 flex items-center gap-3 px-4 py-3 rounded-xl shadow-lg border transition-all duration-300 transform translate-y-2 opacity-0 ${
        type === 'success'
          ? 'bg-emerald-900 text-white border-emerald-700'
          : type === 'error'
          ? 'bg-rose-900 text-white border-rose-700'
          : 'bg-slate-900 text-white border-slate-700'
      }`;

      const icon = type === 'success' ? 'check_circle' : type === 'error' ? 'error' : 'info';
      toast.innerHTML = `
        <span class="material-symbols-outlined text-[20px]">${icon}</span>
        <span class="text-xs font-medium">${message}</span>
        <button class="ml-2 text-white/70 hover:text-white" onclick="this.parentElement.remove()" type="button">
          <span class="material-symbols-outlined text-[16px]">close</span>
        </button>
      `;

      document.body.appendChild(toast);
      requestAnimationFrame(() => {
        toast.classList.remove('translate-y-2', 'opacity-0');
      });

      setTimeout(() => {
        if (toast && toast.parentElement) {
          toast.classList.add('opacity-0', 'translate-y-2');
          setTimeout(() => toast.remove(), 300);
        }
      }, 4000);
    }
  }

  window.NexusAPI = new NexusAPIClient();
})(window);
