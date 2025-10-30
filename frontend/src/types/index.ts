// User types
export interface User {
  id: string;
  email: string;
  created_at: string;
  updated_at: string;
  metadata?: Record<string, any>;
}

// Memory Profile types
export interface MemoryProfile {
  id: string;
  user_id: string;
  name: string;
  description: string | null;
  is_default: boolean;
  created_at: string;
  updated_at: string;
}

export interface MemoryProfileCreate {
  name: string;
  description?: string;
}

export interface MemoryProfileUpdate {
  name?: string;
  description?: string;
}

// Chat Session types
export type PrivacyMode = 'normal' | 'incognito' | 'pause_memories';

export interface ChatSession {
  id: string;
  user_id: string;
  memory_profile_id: string | null;
  privacy_mode: PrivacyMode;
  created_at: string;
  updated_at: string;
}

export interface ChatSessionCreate {
  memory_profile_id?: string | null;
  privacy_mode?: PrivacyMode;
}

export interface ChatSessionUpdate {
  privacy_mode?: PrivacyMode;
}

// Chat Message types
export interface ChatMessage {
  id: string;
  session_id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  created_at: string;
  metadata?: Record<string, any>;
}

export interface ChatMessageCreate {
  role: 'user' | 'assistant' | 'system';
  content: string;
  metadata?: Record<string, any>;
}

// API Request/Response types
export interface ChatRequest {
  message: string;
}

export interface ChatResponse {
  message: ChatMessage;
  response: string;
}

// Memory types
export interface Memory {
  id: string;
  user_id: string;
  memory_profile_id: string;
  mem0_memory_id: string;
  memory_content: string;
  created_at: string;
  updated_at: string;
}

// Auth types
export interface LoginRequest {
  email: string;
  password: string;
}

export interface SignupRequest {
  email: string;
  password: string;
}

export interface AuthResponse {
  user: User;
  session: {
    access_token: string;
    refresh_token: string;
  };
}

// API Error type
export interface APIError {
  message: string;
  details?: any;
}

