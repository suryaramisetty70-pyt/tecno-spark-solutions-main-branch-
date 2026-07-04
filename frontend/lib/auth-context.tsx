/**
 * Authentication Hook - Manage auth state and operations
 */

'use client';

import { createContext, useContext, useState, useEffect } from 'react';
import { apiClient, authAPI } from './api-client';

interface User {
  id: number;
  email: string;
  username: string;
  full_name: string;
  is_active: boolean;
  is_verified: boolean;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  loading: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<boolean>;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load token from localStorage on mount
  useEffect(() => {
    const savedToken = localStorage.getItem('access_token');
    if (savedToken) {
      setToken(savedToken);
      apiClient.setToken(savedToken);
      // Load user profile
      loadUserProfile();
    }
    setLoading(false);
  }, []);

  const loadUserProfile = async () => {
    try {
      const response = await apiClient.get('/api/v1/users/profile');
      if (response.data) {
        setUser(response.data as User);
      }
    } catch (err) {
      console.error('Failed to load profile:', err);
    }
  };

  const login = async (email: string, password: string): Promise<boolean> => {
    try {
      setLoading(true);
      setError(null);

      const response = await authAPI.login(email, password);

      if (response.error) {
        setError(response.error);
        return false;
      }

      const data = response.data as any;
      const newToken = data.access_token || data.token;

      if (newToken) {
        setToken(newToken);
        apiClient.setToken(newToken);
        localStorage.setItem('access_token', newToken);

        // Load user profile
        await loadUserProfile();
        return true;
      }

      return false;
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Login failed';
      setError(errorMsg);
      return false;
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('access_token');
    apiClient.setToken('');
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        loading,
        error,
        login,
        logout,
        isAuthenticated: !!token,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}
