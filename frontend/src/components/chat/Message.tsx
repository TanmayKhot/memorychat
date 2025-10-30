import { useState } from 'react';
import type { ChatMessage } from '../../types';

interface MessageProps {
  message: ChatMessage;
}

const Message = ({ message }: MessageProps) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const isUser = message.role === 'user';
  const timestamp = new Date(message.created_at).toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
  });

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`max-w-[70%] ${isUser ? 'order-2' : 'order-1'}`}>
        <div
          className={`rounded-lg px-4 py-2 ${
            isUser
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-900'
          }`}
        >
          <p className="whitespace-pre-wrap break-words">{message.content}</p>
        </div>
        <div className="flex items-center justify-between mt-1 px-2">
          <span className="text-xs text-gray-500">{timestamp}</span>
          {!isUser && (
            <button
              onClick={handleCopy}
              className="text-xs text-gray-500 hover:text-gray-700"
              title="Copy message"
            >
              {copied ? '✓ Copied' : '📋 Copy'}
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default Message;

