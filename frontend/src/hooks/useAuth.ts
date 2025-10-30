import { useEffect } from 'react';
import { useAuthStore } from '../store/authStore';

/**
 * Custom hook for authentication
 * Provides auth state and methods
 */
export const useAuth = () => {
  const {
    user,
    session,
    isAuthenticated,
    loading,
    error,
    login,
    signup,
    logout,
    checkAuth,
    clearError,
  } = useAuthStore();

  // Check auth status on mount
  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  return {
    user,
    session,
    isAuthenticated,
    loading,
    error,
    login,
    signup,
    logout,
    checkAuth,
    clearError,
  };
};

