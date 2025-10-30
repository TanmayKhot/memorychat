import { useState } from 'react';
import { useAuth } from '../../hooks/useAuth';
import { useChat } from '../../hooks/useChat';
import { useMemoryProfiles } from '../../hooks/useMemoryProfiles';
import Dropdown from '../ui/Dropdown';
import type { PrivacyMode } from '../../types';

const Header = () => {
  const { user, logout } = useAuth();
  const { privacyMode, setPrivacyMode } = useChat();
  const { currentProfile } = useMemoryProfiles();
  const [showUserMenu, setShowUserMenu] = useState(false);

  const privacyModeOptions = [
    { value: 'normal', label: '🔓 Normal' },
    { value: 'incognito', label: '🕵️ Incognito' },
    { value: 'pause_memories', label: '⏸️ Pause Memories' },
  ];

  const handlePrivacyModeChange = (mode: string) => {
    setPrivacyMode(mode as PrivacyMode);
  };

  const getPrivacyModeTooltip = () => {
    switch (privacyMode) {
      case 'normal':
        return 'Memories are being saved and used';
      case 'incognito':
        return 'Messages are not saved to memory';
      case 'pause_memories':
        return 'Existing memories used, but no new ones saved';
      default:
        return '';
    }
  };

  return (
    <header className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <h1 className="text-xl font-bold text-gray-900">MemoryChat</h1>
          
          {currentProfile && (
            <div className="text-sm text-gray-600">
              <span className="font-medium">{currentProfile.name}</span>
            </div>
          )}
        </div>

        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2" title={getPrivacyModeTooltip()}>
            <span className="text-sm text-gray-600">Privacy:</span>
            <Dropdown
              options={privacyModeOptions}
              value={privacyMode}
              onChange={handlePrivacyModeChange}
            />
          </div>

          <div className="relative">
            <button
              onClick={() => setShowUserMenu(!showUserMenu)}
              className="flex items-center space-x-2 px-3 py-2 rounded-lg hover:bg-gray-100"
            >
              <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-white font-semibold">
                {user?.email?.[0].toUpperCase() || 'U'}
              </div>
            </button>

            {showUserMenu && (
              <div className="absolute right-0 mt-2 w-48 bg-white border border-gray-200 rounded-lg shadow-lg py-2 z-10">
                <div className="px-4 py-2 text-sm text-gray-600 border-b border-gray-200">
                  {user?.email}
                </div>
                <button
                  onClick={() => {
                    logout();
                    setShowUserMenu(false);
                  }}
                  className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-gray-100"
                >
                  Logout
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;

