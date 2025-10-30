import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import ProtectedRoute from './components/auth/ProtectedRoute';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Chat from './pages/Chat';
import Settings from './pages/Settings';
import SupabaseDebugPanel from './components/dev/SupabaseDebugPanel';
import './App.css';

function App() {
  return (
    <Router>
      <Routes>
        {/* Public routes */}
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />

        {/* Protected routes */}
        <Route
          path="/chat"
          element={
            <ProtectedRoute>
              <Chat />
            </ProtectedRoute>
          }
        />
        <Route
          path="/settings"
          element={
            <ProtectedRoute>
              <Settings />
            </ProtectedRoute>
          }
        />

        {/* Default route - redirect to chat */}
        <Route path="/" element={<Navigate to="/chat" replace />} />

        {/* Catch all - redirect to chat */}
        <Route path="*" element={<Navigate to="/chat" replace />} />
      </Routes>

      {/* Debug panel - only visible in development */}
      <SupabaseDebugPanel />
    </Router>
  );
}

export default App;
