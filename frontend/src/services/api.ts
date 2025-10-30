import axios from 'axios';
import type { AxiosInstance, AxiosError } from 'axios';
import { API_BASE_URL, API_ENDPOINTS, STORAGE_KEYS } from '../utils/constants';
import { supabase } from './supabase';
import type {
  User,
  MemoryProfile,
  MemoryProfileCreate,
  MemoryProfileUpdate,
  ChatSession,
  ChatSessionCreate,
  ChatSessionUpdate,
  ChatMessage,
  ChatRequest,
  ChatResponse,
  Memory,
  LoginRequest,
  SignupRequest,
  AuthResponse,
} from '../types';

// Create axios instance
const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 second timeout
});

// Request interceptor to add auth token
api.interceptors.request.use(
  async (config) => {
    const { data } = await supabase.auth.getSession();
    const token = data.session?.access_token || localStorage.getItem(STORAGE_KEYS.AUTH_TOKEN) || undefined;
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Handle unauthorized - redirect to login
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  signup: async (data: SignupRequest): Promise<AuthResponse> => {
    const response = await api.post(API_ENDPOINTS.SIGNUP, data);
    return response.data;
  },

  login: async (data: LoginRequest): Promise<AuthResponse> => {
    const response = await api.post(API_ENDPOINTS.LOGIN, data);
    return response.data;
  },

  logout: async (): Promise<void> => {
    await api.post(API_ENDPOINTS.LOGOUT);
  },

  getMe: async (): Promise<User> => {
    const response = await api.get(API_ENDPOINTS.ME);
    return response.data;
  },
};

// Memory Profile API
export const memoryProfileAPI = {
  getAll: async (): Promise<MemoryProfile[]> => {
    const response = await api.get(API_ENDPOINTS.MEMORY_PROFILES);
    return response.data;
  },

  getById: async (id: string): Promise<MemoryProfile> => {
    const response = await api.get(API_ENDPOINTS.MEMORY_PROFILE(id));
    return response.data;
  },

  create: async (data: MemoryProfileCreate): Promise<MemoryProfile> => {
    const response = await api.post(API_ENDPOINTS.MEMORY_PROFILES, data);
    return response.data;
  },

  update: async (id: string, data: MemoryProfileUpdate): Promise<MemoryProfile> => {
    const response = await api.put(API_ENDPOINTS.MEMORY_PROFILE(id), data);
    return response.data;
  },

  delete: async (id: string): Promise<void> => {
    await api.delete(API_ENDPOINTS.MEMORY_PROFILE(id));
  },

  setDefault: async (id: string): Promise<void> => {
    await api.post(API_ENDPOINTS.SET_DEFAULT_PROFILE(id));
  },

  getMemories: async (id: string): Promise<Memory[]> => {
    const response = await api.get(API_ENDPOINTS.PROFILE_MEMORIES(id));
    return response.data;
  },
};

// Session API
export const sessionAPI = {
  getAll: async (): Promise<ChatSession[]> => {
    const response = await api.get(API_ENDPOINTS.SESSIONS);
    return response.data;
  },

  getById: async (id: string): Promise<ChatSession> => {
    const response = await api.get(API_ENDPOINTS.SESSION(id));
    return response.data;
  },

  create: async (data: ChatSessionCreate): Promise<ChatSession> => {
    const response = await api.post(API_ENDPOINTS.SESSIONS, data);
    return response.data;
  },

  update: async (id: string, data: ChatSessionUpdate): Promise<ChatSession> => {
    const response = await api.put(API_ENDPOINTS.SESSION(id), data);
    return response.data;
  },

  delete: async (id: string): Promise<void> => {
    await api.delete(API_ENDPOINTS.SESSION(id));
  },

  getMessages: async (id: string): Promise<ChatMessage[]> => {
    const response = await api.get(API_ENDPOINTS.SESSION_MESSAGES(id));
    return response.data;
  },
};

// Chat API
export const chatAPI = {
  sendMessage: async (sessionId: string, message: string): Promise<ChatResponse> => {
    const response = await api.post(API_ENDPOINTS.CHAT(sessionId), {
      message,
    } as ChatRequest);
    return response.data;
  },

  // Stream message (for future implementation)
  streamMessage: async (sessionId: string, message: string): Promise<ReadableStream> => {
    const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.CHAT_STREAM(sessionId)}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${(await supabase.auth.getSession()).data.session?.access_token}`,
      },
      body: JSON.stringify({ message } as ChatRequest),
    });
    
    if (!response.ok) {
      throw new Error('Failed to stream message');
    }
    
    return response.body!;
  },
};

export default api;

