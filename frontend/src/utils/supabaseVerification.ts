import { supabase, testSupabaseConnection } from '../services/supabase';
import { SUPABASE_URL, SUPABASE_ANON_KEY } from './constants';

/**
 * Verify Supabase configuration and connection
 * This function checks if all required environment variables are set
 * and tests the connection to Supabase.
 */
export const verifySupabaseSetup = async (): Promise<{
  success: boolean;
  errors: string[];
  warnings: string[];
}> => {
  const errors: string[] = [];
  const warnings: string[] = [];

  // Check environment variables
  if (!SUPABASE_URL) {
    errors.push('VITE_SUPABASE_URL is not set');
  } else if (!SUPABASE_URL.startsWith('https://')) {
    warnings.push('VITE_SUPABASE_URL should start with https://');
  }

  if (!SUPABASE_ANON_KEY) {
    errors.push('VITE_SUPABASE_ANON_KEY is not set');
  } else if (SUPABASE_ANON_KEY.length < 100) {
    warnings.push('VITE_SUPABASE_ANON_KEY seems too short');
  }

  // Test connection if variables are set
  if (errors.length === 0) {
    try {
      const connectionSuccess = await testSupabaseConnection();
      if (!connectionSuccess) {
        errors.push('Failed to connect to Supabase');
      }
    } catch (error) {
      errors.push(`Connection error: ${error}`);
    }
  }

  // Check if client is properly initialized
  if (!supabase) {
    errors.push('Supabase client is not initialized');
  }

  return {
    success: errors.length === 0,
    errors,
    warnings,
  };
};

/**
 * Log Supabase configuration status
 * Useful for debugging during development
 */
export const logSupabaseStatus = async () => {
  console.group('🔧 Supabase Configuration Status');
  
  console.log('Environment:', import.meta.env.MODE);
  console.log('URL:', SUPABASE_URL ? '✅ Set' : '❌ Missing');
  console.log('Anon Key:', SUPABASE_ANON_KEY ? '✅ Set' : '❌ Missing');
  
  const { success, errors, warnings } = await verifySupabaseSetup();
  
  if (success) {
    console.log('✅ Supabase is properly configured and connected');
  } else {
    console.error('❌ Supabase configuration has errors:');
    errors.forEach(error => console.error(`  - ${error}`));
  }
  
  if (warnings.length > 0) {
    console.warn('⚠️  Warnings:');
    warnings.forEach(warning => console.warn(`  - ${warning}`));
  }
  
  console.groupEnd();
};

/**
 * Check if user is authenticated
 */
export const checkAuth = async (): Promise<boolean> => {
  try {
    const { data } = await supabase.auth.getSession();
    return !!data.session;
  } catch (error) {
    console.error('Error checking auth:', error);
    return false;
  }
};

