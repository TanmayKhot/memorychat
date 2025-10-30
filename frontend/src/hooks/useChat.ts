import { useChatStore } from '../store/chatStore';

/**
 * Custom hook for chat operations
 * Provides chat state and methods
 */
export const useChat = () => {
  const {
    currentSession,
    messages,
    isLoading,
    error,
    privacyMode,
    setCurrentSession,
    createSession,
    loadSession,
    loadMessages,
    sendMessage,
    addMessage,
    setPrivacyMode,
    clearMessages,
    deleteSession,
  } = useChatStore();

  return {
    currentSession,
    messages,
    isLoading,
    error,
    privacyMode,
    setCurrentSession,
    createSession,
    loadSession,
    loadMessages,
    sendMessage,
    addMessage,
    setPrivacyMode,
    clearMessages,
    deleteSession,
  };
};

