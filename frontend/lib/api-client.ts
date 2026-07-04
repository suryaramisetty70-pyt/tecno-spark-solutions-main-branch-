/**
 * API Client - Central service for backend communication
 */

export const API_BASE_URL =
process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';
export interface ApiResponse<T> {
  data?: T;
  error?: string;
  message?: string;
  status?: number;
}

class ApiClient {
  private token: string | null = null;

  setToken(token: string) {
    this.token = token;
  }

  getToken(): string | null {
    return this.token;
  }

  private getHeaders(): HeadersInit {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    return headers;
  }

  async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    try {
      const url = `${API_BASE_URL}${endpoint}`;
      const response = await fetch(url, {
        ...options,
        headers: this.getHeaders(),
      });

      const data = await response.json();

      if (!response.ok) {
        return {
          error: data.detail || data.message || 'An error occurred',
          status: response.status,
        };
      }

      return { data };
    } catch (error) {
      return {
        error: error instanceof Error ? error.message : 'Network error',
      };
    }
  }

  async get<T>(endpoint: string): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { method: 'GET' });
  }

  async post<T>(endpoint: string, body: any): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: JSON.stringify(body),
    });
  }

  async put<T>(endpoint: string, body: any): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: JSON.stringify(body),
    });
  }

  async delete<T>(endpoint: string): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { method: 'DELETE' });
  }
}

export const apiClient = new ApiClient();

// Auth endpoints
export const authAPI = {
  login: (email: string, password: string) =>
    apiClient.post('/api/v1/auth/login', { email, password }),
  logout: () => apiClient.post('/api/v1/auth/logout', {}),
  refreshToken: () => apiClient.post('/api/v1/auth/refresh', {}),
};

// User endpoints
export const userAPI = {
  getProfile: () => apiClient.get('/api/v1/users/profile'),
  updateProfile: (data: any) => apiClient.put('/api/v1/users/profile', data),
  getPreferences: () => apiClient.get('/api/v1/users/preferences'),
  updatePreferences: (data: any) => apiClient.put('/api/v1/users/preferences', data),
  getGoals: (skip = 0, limit = 20) =>
    apiClient.get(`/api/v1/users/goals?skip=${skip}&limit=${limit}`),
  createGoal: (data: any) => apiClient.post('/api/v1/users/goals', data),
  getActivity: () => apiClient.get('/api/v1/users/activity'),
};

// Workflow endpoints
export const workflowAPI = {
  list: (skip = 0, limit = 20) =>
    apiClient.get(`/api/v1/workflows?skip=${skip}&limit=${limit}`),
  get: (id: number) => apiClient.get(`/api/v1/workflows/${id}`),
  create: (data: any) => apiClient.post('/api/v1/workflows', data),
  update: (id: number, data: any) => apiClient.put(`/api/v1/workflows/${id}`, data),
  delete: (id: number) => apiClient.delete(`/api/v1/workflows/${id}`),
  execute: (id: number) => apiClient.post(`/api/v1/workflows/${id}/execute`, {}),
  getExecutions: (id: number, skip = 0, limit = 20) =>
    apiClient.get(`/api/v1/workflows/${id}/executions?skip=${skip}&limit=${limit}`),
};

// Agent endpoints
export const agentAPI = {
  list: (skip = 0, limit = 20) =>
    apiClient.get(`/api/v1/agents?skip=${skip}&limit=${limit}`),
  get: (id: number) => apiClient.get(`/api/v1/agents/${id}`),
  create: (data: any) => apiClient.post('/api/v1/agents', data),
  update: (id: number, data: any) => apiClient.put(`/api/v1/agents/${id}`, data),
  getMetrics: (id: number) => apiClient.get(`/api/v1/agents/${id}/metrics`),
  getStatus: (id: number) => apiClient.get(`/api/v1/agents/${id}/status`),
};

// File endpoints
export const fileAPI = {
  list: (skip = 0, limit = 20) =>
    apiClient.get(`/api/v1/files?skip=${skip}&limit=${limit}`),
  get: (id: number) => apiClient.get(`/api/v1/files/${id}`),
  delete: (id: number) => apiClient.delete(`/api/v1/files/${id}`),
  search: (query: string) =>
    apiClient.post('/api/v1/files/search', { query, skip: 0, limit: 20 }),
  getMetadata: (id: number) => apiClient.get(`/api/v1/files/${id}/metadata`),
};

// Search endpoints
export const searchAPI = {
  global: (query: string, entityTypes: string[] = []) =>
    apiClient.post('/api/v1/search/global', {
      query,
      entity_types: entityTypes,
      filters: [],
      skip: 0,
      limit: 20,
    }),
  advanced: (params: any) => apiClient.post('/api/v1/search/advanced', params),
  saveSearch: (data: any) => apiClient.post('/api/v1/search/saved', data),
  getSavedSearches: () => apiClient.get('/api/v1/search/saved'),
  getSuggestions: (query: string) =>
    apiClient.post('/api/v1/search/suggestions', { query, limit: 10 }),
  getRecommendations: (entityType: string) =>
    apiClient.post('/api/v1/search/discover', { entity_type: entityType, limit: 10 }),
};

// Analytics endpoints
export const analyticsAPI = {
  getUserAnalytics: () => apiClient.get('/api/v1/analytics/user'),
  getDashboard: () => apiClient.get('/api/v1/analytics/dashboard'),
  getWorkflowMetrics: (id: number) => apiClient.get(`/api/v1/analytics/workflows/${id}`),
  getAgentMetrics: (id: number) => apiClient.get(`/api/v1/analytics/agents/${id}`),
  getHealth: () => apiClient.get('/api/v1/analytics/health'),
};

// Notification endpoints
export const notificationAPI = {
  list: (skip = 0, limit = 20) =>
    apiClient.get(`/api/v1/notifications?skip=${skip}&limit=${limit}`),
  get: (id: number) => apiClient.get(`/api/v1/notifications/${id}`),
  markAsRead: (id: number) => apiClient.put(`/api/v1/notifications/${id}/read`, {}),
  delete: (id: number) => apiClient.delete(`/api/v1/notifications/${id}`),
  getStats: () => apiClient.get('/api/v1/notifications/stats'),
};
