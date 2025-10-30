import { useEffect, useState } from 'react';
import { verifySupabaseSetup } from '../../utils/supabaseVerification';
import { supabase } from '../../services/supabase';

/**
 * Debug panel for Supabase connection status
 * Only visible in development mode
 */
const SupabaseDebugPanel = () => {
  const [status, setStatus] = useState<{
    success: boolean;
    errors: string[];
    warnings: string[];
  } | null>(null);
  const [session, setSession] = useState<any>(null);
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const checkStatus = async () => {
      const result = await verifySupabaseSetup();
      setStatus(result);

      const { data } = await supabase.auth.getSession();
      setSession(data.session);
    };

    checkStatus();
  }, []);

  // Only show in development mode
  if (import.meta.env.PROD) {
    return null;
  }

  if (!isVisible) {
    return (
      <button
        onClick={() => setIsVisible(true)}
        className="fixed bottom-4 right-4 bg-blue-600 text-white px-4 py-2 rounded-lg shadow-lg hover:bg-blue-700 text-sm z-50"
        title="Show Supabase Debug Panel"
      >
        🔧 Debug
      </button>
    );
  }

  return (
    <div className="fixed bottom-4 right-4 bg-white border-2 border-gray-300 rounded-lg shadow-xl p-4 max-w-md z-50">
      <div className="flex justify-between items-center mb-3">
        <h3 className="font-bold text-lg">🔧 Supabase Debug</h3>
        <button
          onClick={() => setIsVisible(false)}
          className="text-gray-500 hover:text-gray-700 text-xl leading-none"
        >
          ×
        </button>
      </div>

      {status && (
        <div className="space-y-3">
          <div>
            <p className="text-sm font-semibold mb-1">Connection Status:</p>
            <p className={`text-sm ${status.success ? 'text-green-600' : 'text-red-600'}`}>
              {status.success ? '✅ Connected' : '❌ Not Connected'}
            </p>
          </div>

          {status.errors.length > 0 && (
            <div>
              <p className="text-sm font-semibold mb-1 text-red-600">Errors:</p>
              <ul className="text-sm text-red-600 list-disc list-inside">
                {status.errors.map((error, i) => (
                  <li key={i}>{error}</li>
                ))}
              </ul>
            </div>
          )}

          {status.warnings.length > 0 && (
            <div>
              <p className="text-sm font-semibold mb-1 text-yellow-600">Warnings:</p>
              <ul className="text-sm text-yellow-600 list-disc list-inside">
                {status.warnings.map((warning, i) => (
                  <li key={i}>{warning}</li>
                ))}
              </ul>
            </div>
          )}

          <div>
            <p className="text-sm font-semibold mb-1">Session:</p>
            <p className="text-sm">
              {session ? (
                <>
                  ✅ Active
                  <br />
                  <span className="text-xs text-gray-600">
                    User: {session.user?.email}
                  </span>
                </>
              ) : (
                '❌ No active session'
              )}
            </p>
          </div>

          <div>
            <p className="text-sm font-semibold mb-1">Environment:</p>
            <p className="text-xs text-gray-600">
              Mode: {import.meta.env.MODE}
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default SupabaseDebugPanel;

