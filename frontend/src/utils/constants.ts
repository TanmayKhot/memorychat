// API Base URL (ensure it targets the backend API version path)
const API_ORIGIN = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/$/, '');
const API_BASE_PATH = (import.meta.env.VITE_API_BASE_PATH || '/api/v1').replace(/\/$/, '');
export const API_BASE_URL = `${API_ORIGIN}${API_BASE_PATH}`;

// Supabase Configuration
export const SUPABASE_URL = import.meta.env.VITE_SUPABASE_URL || '';
export const SUPABASE_ANON_KEY = import.meta.env.VITE_SUPABASE_ANON_KEY || '';

// Local Storage Keys
export const STORAGE_KEYS = {
  AUTH_TOKEN: 'memorychat_auth_token',
  CURRENT_PROFILE: 'memorychat_current_profile',
  PRIVACY_MODE: 'memorychat_privacy_mode',
} as const;

// Privacy Mode Options
export const PRIVACY_MODES = {
  NORMAL: 'normal',
  INCOGNITO: 'incognito',
  PAUSE_MEMORIES: 'pause_memories',
} as const;

// API Endpoints
export const API_ENDPOINTS = {
  // Auth
  SIGNUP: '/auth/signup',
  LOGIN: '/auth/login',
  LOGOUT: '/auth/logout',
  ME: '/auth/me',
  
  // Memory Profiles
  MEMORY_PROFILES: '/memory-profiles',
  MEMORY_PROFILE: (id: string) => `/memory-profiles/${id}`,
  SET_DEFAULT_PROFILE: (id: string) => `/memory-profiles/${id}/set-default`,
  PROFILE_MEMORIES: (id: string) => `/memory-profiles/${id}/memories`,
  
  // Sessions
  SESSIONS: '/sessions',
  SESSION: (id: string) => `/sessions/${id}`,
  SESSION_MESSAGES: (id: string) => `/sessions/${id}/messages`,
  
  // Chat
  CHAT: (sessionId: string) => `/chat/${sessionId}`,
  CHAT_STREAM: (sessionId: string) => `/chat/${sessionId}/stream`,
} as const;

// UI Constants
export const MAX_MESSAGE_LENGTH = 4000;
export const CHAT_INPUT_PLACEHOLDER = 'Type your message... (Enter to send, Shift+Enter for new line)';

