import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useChat } from '../../hooks/useChat';
import { useMemoryProfiles } from '../../hooks/useMemoryProfiles';
import Button from '../ui/Button';
import MemoryProfileSelector from '../memory/MemoryProfileSelector';
import type { ChatSession } from '../../types';

const Sidebar = () => {
  const [sessions] = useState<ChatSession[]>([]);
  const [loading, setLoading] = useState(false);
  const { createSession, currentSession } = useChat();
  const { currentProfile } = useMemoryProfiles();
  const navigate = useNavigate();

  useEffect(() => {
    // Load sessions when sidebar mounts
    // This would connect to the API
    loadSessions();
  }, [currentProfile]);

  const loadSessions = async () => {
    setLoading(true);
    try {
      // TODO: Load sessions from API
      // const loadedSessions = await api.getSessions();
      // setSessions(loadedSessions);
    } catch (error) {
      console.error('Failed to load sessions:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleNewChat = async () => {
    try {
      const newSession = await createSession(currentProfile?.id || null);
      navigate(`/chat?session=${newSession.id}`);
    } catch (error) {
      console.error('Failed to create session:', error);
    }
  };

  return (
    <div className="w-64 bg-white border-r border-gray-200 flex flex-col">
      <div className="p-4 border-b border-gray-200">
        <Button onClick={handleNewChat} className="w-full">
          + New Chat
        </Button>
      </div>

      <div className="p-4 border-b border-gray-200">
        <MemoryProfileSelector />
      </div>

      <div className="flex-1 overflow-y-auto p-4">
        <h3 className="text-sm font-semibold text-gray-600 mb-2">Recent Chats</h3>
        
        {loading ? (
          <div className="text-sm text-gray-500">Loading...</div>
        ) : sessions.length === 0 ? (
          <div className="text-sm text-gray-500">No chat history</div>
        ) : (
          <div className="space-y-2">
            {sessions.map((session) => (
              <button
                key={session.id}
                onClick={() => navigate(`/chat?session=${session.id}`)}
                className={`w-full text-left px-3 py-2 rounded-lg text-sm hover:bg-gray-100 ${
                  currentSession?.id === session.id ? 'bg-gray-100' : ''
                }`}
              >
                <div className="truncate">
                  {new Date(session.created_at).toLocaleDateString()}
                </div>
              </button>
            ))}
          </div>
        )}
      </div>

      <div className="p-4 border-t border-gray-200">
        <button
          onClick={() => navigate('/settings')}
          className="w-full text-left px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-lg"
        >
          ⚙️ Settings
        </button>
      </div>
    </div>
  );
};

export default Sidebar;

