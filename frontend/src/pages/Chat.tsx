import { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useChat } from '../hooks/useChat';
import { useMemoryProfiles } from '../hooks/useMemoryProfiles';
import Layout from '../components/layout/Layout';
import ChatInterface from '../components/chat/ChatInterface';

const Chat = () => {
  const [searchParams] = useSearchParams();
  const sessionId = searchParams.get('session');
  const { currentSession, loadSession, createSession } = useChat();
  const { currentProfile } = useMemoryProfiles();
  const [initialized, setInitialized] = useState(false);

  useEffect(() => {
    const initializeChat = async () => {
      if (initialized) return;

      try {
        if (sessionId) {
          // Load existing session
          await loadSession(sessionId);
        } else if (!currentSession && currentProfile) {
          // Create new session with current profile
          await createSession(currentProfile.id);
        }
        setInitialized(true);
      } catch (error) {
        console.error('Failed to initialize chat:', error);
      }
    };

    if (currentProfile) {
      initializeChat();
    }
  }, [sessionId, currentSession, currentProfile, loadSession, createSession, initialized]);

  return (
    <Layout showSidebar={true}>
      <div className="h-full bg-white">
        <ChatInterface sessionId={currentSession?.id || null} />
      </div>
    </Layout>
  );
};

export default Chat;

