import { useEffect } from 'react';
import { useChat } from '../../hooks/useChat';
import MessageList from './MessageList';
import MessageInput from './MessageInput';

interface ChatInterfaceProps {
  sessionId: string | null;
}

const ChatInterface = ({ sessionId }: ChatInterfaceProps) => {
  const { messages, isLoading, privacyMode, sendMessage, loadMessages } = useChat();

  useEffect(() => {
    if (sessionId) {
      loadMessages(sessionId);
    }
  }, [sessionId, loadMessages]);

  const handleSendMessage = async (content: string) => {
    if (!sessionId) return;
    await sendMessage(sessionId, content);
  };

  const getPrivacyModeIndicator = () => {
    switch (privacyMode) {
      case 'incognito':
        return (
          <div className="bg-purple-100 border border-purple-300 text-purple-800 px-4 py-2 rounded-lg text-sm">
            🕵️ Incognito Mode: Messages are not saved to memory
          </div>
        );
      case 'pause_memories':
        return (
          <div className="bg-yellow-100 border border-yellow-300 text-yellow-800 px-4 py-2 rounded-lg text-sm">
            ⏸️ Memories Paused: Existing memories used, but no new ones saved
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div className="flex flex-col h-full">
      {getPrivacyModeIndicator() && (
        <div className="px-4 py-2">
          {getPrivacyModeIndicator()}
        </div>
      )}
      
      <div className="flex-1 overflow-hidden">
        <MessageList messages={messages} isLoading={isLoading} />
      </div>
      
      <div className="border-t border-gray-200 p-4">
        <MessageInput 
          onSend={handleSendMessage} 
          disabled={!sessionId || isLoading}
        />
      </div>
    </div>
  );
};

export default ChatInterface;

