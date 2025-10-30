import { create } from 'zustand';
import { memoryProfileAPI } from '../services/api';
import type { MemoryProfile, MemoryProfileCreate, MemoryProfileUpdate } from '../types';

interface MemoryState {
  profiles: MemoryProfile[];
  currentProfile: MemoryProfile | null;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  fetchProfiles: () => Promise<void>;
  createProfile: (data: MemoryProfileCreate) => Promise<MemoryProfile>;
  updateProfile: (id: string, data: MemoryProfileUpdate) => Promise<MemoryProfile>;
  deleteProfile: (id: string) => Promise<void>;
  setCurrentProfile: (profileId: string) => Promise<void>;
  setDefaultProfile: (id: string) => Promise<void>;
  clearError: () => void;
}

export const useMemoryStore = create<MemoryState>((set, get) => ({
  profiles: [],
  currentProfile: null,
  isLoading: false,
  error: null,

  fetchProfiles: async () => {
    try {
      set({ isLoading: true, error: null });
      const profiles = await memoryProfileAPI.getAll();
      
      // Find default profile
      const defaultProfile = profiles.find(p => p.is_default) || profiles[0] || null;
      
      set({
        profiles,
        currentProfile: defaultProfile,
        isLoading: false,
      });
    } catch (error: any) {
      set({ error: error.message, isLoading: false });
      throw error;
    }
  },

  createProfile: async (data: MemoryProfileCreate) => {
    try {
      set({ isLoading: true, error: null });
      const newProfile = await memoryProfileAPI.create(data);
      
      set(state => ({
        profiles: [...state.profiles, newProfile],
        isLoading: false,
      }));
      
      return newProfile;
    } catch (error: any) {
      set({ error: error.message, isLoading: false });
      throw error;
    }
  },

  updateProfile: async (id: string, data: MemoryProfileUpdate) => {
    try {
      set({ isLoading: true, error: null });
      const updatedProfile = await memoryProfileAPI.update(id, data);
      
      set(state => ({
        profiles: state.profiles.map(p => p.id === id ? updatedProfile : p),
        currentProfile: state.currentProfile?.id === id ? updatedProfile : state.currentProfile,
        isLoading: false,
      }));
      
      return updatedProfile;
    } catch (error: any) {
      set({ error: error.message, isLoading: false });
      throw error;
    }
  },

  deleteProfile: async (id: string) => {
    const { profiles } = get();
    
    if (profiles.length <= 1) {
      throw new Error('Cannot delete the only profile');
    }

    try {
      set({ isLoading: true, error: null });
      await memoryProfileAPI.delete(id);
      
      const remainingProfiles = profiles.filter(p => p.id !== id);
      const newCurrentProfile = remainingProfiles.find(p => p.is_default) || remainingProfiles[0];
      
      set({
        profiles: remainingProfiles,
        currentProfile: newCurrentProfile,
        isLoading: false,
      });
    } catch (error: any) {
      set({ error: error.message, isLoading: false });
      throw error;
    }
  },

  setCurrentProfile: async (profileId: string) => {
    const { profiles } = get();
    const profile = profiles.find(p => p.id === profileId);
    
    if (profile) {
      set({ currentProfile: profile });
    }
  },

  setDefaultProfile: async (id: string) => {
    try {
      set({ isLoading: true, error: null });
      await memoryProfileAPI.setDefault(id);
      
      // Refresh profiles to get updated default status
      await get().fetchProfiles();
    } catch (error: any) {
      set({ error: error.message, isLoading: false });
      throw error;
    }
  },

  clearError: () => {
    set({ error: null });
  },
}));

