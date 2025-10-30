import { create } from 'zustand';
import { sessionAPI, chatAPI } from '../services/api';
import type { ChatSession, ChatMessage, PrivacyMode } from '../types';

interface ChatState {
  currentSession: ChatSession | null;
  messages: ChatMessage[];
  isLoading: boolean;
  error: string | null;
  privacyMode: PrivacyMode;
  
  // Actions
  setCurrentSession: (session: ChatSession | null) => void;
  createSession: (memoryProfileId: string | null, privacyMode?: PrivacyMode) => Promise<ChatSession>;
  loadSession: (sessionId: string) => Promise<void>;
  loadMessages: (sessionId: string) => Promise<void>;
  sendMessage: (sessionId: string, content: string) => Promise<void>;
  addMessage: (message: ChatMessage) => void;
  setPrivacyMode: (mode: PrivacyMode) => Promise<void>;
  clearMessages: () => void;
  clearChat: () => void;
  deleteSession: (sessionId: string) => Promise<void>;
}

export const useChatStore = create<ChatState>((set, get) => ({
  currentSession: null,
  messages: [],
  isLoading: false,
  error: null,
  privacyMode: 'normal' as PrivacyMode,

  setCurrentSession: (session: ChatSession | null) => {
    set({ 
      currentSession: session,
      privacyMode: session?.privacy_mode || 'normal' as PrivacyMode,
    });
  },

  createSession: async (memoryProfileId: string | null, privacyMode: PrivacyMode = 'normal' as PrivacyMode) => {
    try {
      set({ isLoading: true, error: null });
      const session = await sessionAPI.create({
        memory_profile_id: memoryProfileId,
        privacy_mode: privacyMode,
      });
      
      set({
        currentSession: session,
        messages: [],
        privacyMode: session.privacy_mode,
        isLoading: false,
      });
      
      return session;
    } catch (error: any) {
      set({ error: error.message, isLoading: false });
      throw error;
    }
  },

  loadSession: async (sessionId: string) => {
    try {
      set({ isLoading: true, error: null });
      const session = await sessionAPI.getById(sessionId);
      const messages = await sessionAPI.getMessages(sessionId);
      
      set({
        currentSession: session,
        messages,
        privacyMode: session.privacy_mode,
        isLoading: false,
      });
    } catch (error: any) {
      set({ error: error.message, isLoading: false });
      throw error;
    }
  },

  loadMessages: async (sessionId: string) => {
    try {
      set({ isLoading: true, error: null });
      const messages = await sessionAPI.getMessages(sessionId);
      set({ messages, isLoading: false });
    } catch (error: any) {
      set({ error: error.message, isLoading: false });
      throw error;
    }
  },

  sendMessage: async (sessionId: string, content: string) => {
    try {
      set({ isLoading: true, error: null });
      
      // Add user message to UI immediately
      const userMessage: ChatMessage = {
        id: Date.now().toString(), // Temporary ID
        session_id: sessionId,
        role: 'user',
        content,
        created_at: new Date().toISOString(),
      };
      
      set(state => ({
        messages: [...state.messages, userMessage],
      }));
      
      // Send message to API
      const response = await chatAPI.sendMessage(sessionId, content);
      
      // Replace temporary message with actual messages from API
      set(state => ({
        messages: [
          ...state.messages.filter(m => m.id !== userMessage.id),
          response.message,
          {
            id: Date.now().toString(),
            session_id: sessionId,
            role: 'assistant' as const,
            content: response.response,
            created_at: new Date().toISOString(),
          },
        ],
        isLoading: false,
      }));
    } catch (error: any) {
      set({ error: error.message, isLoading: false });
      throw error;
    }
  },

  addMessage: (message: ChatMessage) => {
    set(state => ({
      messages: [...state.messages, message],
    }));
  },

  setPrivacyMode: async (mode: PrivacyMode) => {
    const { currentSession } = get();
    if (!currentSession) return;

    try {
      set({ isLoading: true, error: null });
      const updatedSession = await sessionAPI.update(currentSession.id, {
        privacy_mode: mode,
      });
      
      set({
        currentSession: updatedSession,
        privacyMode: mode,
        isLoading: false,
      });
    } catch (error: any) {
      set({ error: error.message, isLoading: false });
      throw error;
    }
  },

  clearMessages: () => {
    set({ messages: [] });
  },

  clearChat: () => {
    set({ messages: [] });
  },

  deleteSession: async (sessionId: string) => {
    try {
      set({ isLoading: true, error: null });
      await sessionAPI.delete(sessionId);
      
      const { currentSession } = get();
      if (currentSession?.id === sessionId) {
        set({ currentSession: null, messages: [] });
      }
      
      set({ isLoading: false });
    } catch (error: any) {
      set({ error: error.message, isLoading: false });
      throw error;
    }
  },
}));

