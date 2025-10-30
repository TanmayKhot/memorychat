import { useEffect } from 'react';
import type { ReactNode } from 'react';
import { supabase } from '../../services/supabase';
import { useAuthStore } from '../../store/authStore';
// import { logSupabaseStatus } from '../../utils/supabaseVerification';

interface AuthProviderProps {
  children: ReactNode;
}

/**
 * AuthProvider component that listens to Supabase auth state changes
 * and updates the application's auth store accordingly.
 * 
 * This provider should wrap the entire application to ensure
 * auth state is properly synchronized across the app.
 */
const AuthProvider = ({ children }: AuthProviderProps) => {
  const { checkAuth, setUser } = useAuthStore();

  useEffect(() => {
    // Log Supabase status in development
    // Temporarily disabled
    // if (import.meta.env.DEV) {
    //   logSupabaseStatus();
    // }

    // Check for existing session on mount
    const initializeAuth = async () => {
      try {
        await checkAuth();
      } catch (error) {
        console.error('Failed to initialize auth:', error);
      }
    };

    initializeAuth();

    // Set up auth state listener
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      async (event, session) => {
        if (import.meta.env.DEV) {
          console.log('🔐 Auth state changed:', event, session?.user?.email);
        }

        try {
          switch (event) {
            case 'INITIAL_SESSION':
              // Initial session loaded
              if (session?.user) {
                await checkAuth();
              }
              break;

            case 'SIGNED_IN':
              // User has signed in
              if (session?.user) {
                await checkAuth();
              }
              break;

            case 'SIGNED_OUT':
              // User has signed out
              setUser(null);
              // Clear any stored tokens
              localStorage.clear();
              break;

            case 'TOKEN_REFRESHED':
              // Token was refreshed - update session
              if (session?.user) {
                await checkAuth();
              }
              break;

            case 'USER_UPDATED':
              // User data was updated
              if (session?.user) {
                await checkAuth();
              }
              break;

            case 'PASSWORD_RECOVERY':
              // User is recovering password
              console.log('Password recovery initiated');
              break;

            default:
              break;
          }
        } catch (error) {
          console.error('Error handling auth state change:', error);
        }
      }
    );

    // Cleanup subscription on unmount
    return () => {
      subscription.unsubscribe();
    };
  }, [checkAuth, setUser]);

  // Show loading indicator while initializing
  // Temporarily disabled - render immediately
  // if (!isInitialized) {
  //   return (
  //     <div className="flex items-center justify-center min-h-screen bg-gray-50">
  //       <div className="text-center">
  //         <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
  //         <p className="text-gray-600">Initializing...</p>
  //       </div>
  //     </div>
  //   );
  // }

  return <>{children}</>;
};

export default AuthProvider;

