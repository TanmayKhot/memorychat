import { create } from 'zustand';
import { authAPI } from '../services/api';
import { STORAGE_KEYS } from '../utils/constants';
import type { User } from '../types';

interface AuthState {
  user: User | null;
  session: any | null;
  isAuthenticated: boolean;
  loading: boolean;
  error: string | null;
  
  // Actions
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  checkAuth: () => Promise<void>;
  setUser: (user: User | null) => void;
  clearError: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  session: null,
  isAuthenticated: false,
  loading: true,
  error: null,

  login: async (email: string, password: string) => {
    try {
      set({ loading: true, error: null });
      const resp: any = await authAPI.login({ email, password });
      const accessToken: string | undefined = resp?.access_token;
      if (accessToken) {
        localStorage.setItem(STORAGE_KEYS.AUTH_TOKEN, accessToken);
      }
      if (accessToken) {
        const user = await authAPI.getMe();
        set({
          user,
          session: { access_token: accessToken },
          isAuthenticated: true,
          loading: false,
        });
      } else {
        // No session returned on signup (email confirmation likely required)
        set({ loading: false });
      }
    } catch (error: any) {
      set({ error: error.message, loading: false });
      throw error;
    }
  },

  signup: async (email: string, password: string) => {
    try {
      set({ loading: true, error: null });
      console.log('Starting signup...');
      const resp: any = await authAPI.signup({ email, password });
      console.log('Signup response:', resp);
      const accessToken: string | undefined = resp?.access_token;
      if (accessToken) {
        localStorage.setItem(STORAGE_KEYS.AUTH_TOKEN, accessToken);
        console.log('Token saved, fetching user...');
      }
      const user = await authAPI.getMe();
      console.log('User fetched:', user);
      set({
        user,
        session: { access_token: accessToken },
        isAuthenticated: true,
        loading: false,
      });
    } catch (error: any) {
      console.error('Signup error:', error);
      set({ error: error.message, loading: false });
      throw error;
    }
  },

  logout: async () => {
    try {
      set({ loading: true });
      localStorage.removeItem(STORAGE_KEYS.AUTH_TOKEN);
      await authAPI.logout().catch(() => {});
      set({
        user: null,
        session: null,
        isAuthenticated: false,
        loading: false,
      });
    } catch (error: any) {
      set({ error: error.message, loading: false });
      throw error;
    }
  },

  checkAuth: async () => {
    try {
      set({ loading: true });
      const token = localStorage.getItem(STORAGE_KEYS.AUTH_TOKEN);
      if (token) {
        const user = await authAPI.getMe();
        set({
          user,
          session: { access_token: token },
          isAuthenticated: true,
          loading: false,
        });
        return;
      }
      // Fallback: treat as logged out
      set({
        user: null,
        session: null,
        isAuthenticated: false,
        loading: false,
      });
    } catch (error) {
      set({
        user: null,
        session: null,
        isAuthenticated: false,
        loading: false,
      });
    }
  },

  setUser: (user: User | null) => {
    set({ user, isAuthenticated: !!user });
  },

  clearError: () => {
    set({ error: null });
  },
}));

