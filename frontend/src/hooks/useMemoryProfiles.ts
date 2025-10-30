import { useEffect } from 'react';
import { useMemoryStore } from '../store/memoryStore';

/**
 * Custom hook for memory profile operations
 * Provides memory profile state and methods
 */
export const useMemoryProfiles = () => {
  const {
    profiles,
    currentProfile,
    isLoading,
    error,
    fetchProfiles,
    createProfile,
    updateProfile,
    deleteProfile,
    setCurrentProfile,
    setDefaultProfile,
    clearError,
  } = useMemoryStore();

  // Fetch profiles on mount
  useEffect(() => {
    if (profiles.length === 0) {
      fetchProfiles();
    }
  }, [profiles.length, fetchProfiles]);

  return {
    profiles,
    currentProfile,
    isLoading,
    error,
    fetchProfiles,
    createProfile,
    updateProfile,
    deleteProfile,
    setCurrentProfile,
    setDefaultProfile,
    clearError,
  };
};

