import { useMemoryProfiles } from '../../hooks/useMemoryProfiles';
import Dropdown from '../ui/Dropdown';

interface MemoryProfileSelectorProps {
  onProfileChange?: (profileId: string) => void;
}

const MemoryProfileSelector = ({ onProfileChange }: MemoryProfileSelectorProps) => {
  const { profiles, currentProfile, setCurrentProfile, isLoading } = useMemoryProfiles();

  const handleChange = async (profileId: string) => {
    const confirmed = window.confirm(
      'Switching memory profiles will start a new chat session. Continue?'
    );
    
    if (confirmed) {
      await setCurrentProfile(profileId);
      onProfileChange?.(profileId);
    }
  };

  if (isLoading) {
    return <div className="text-sm text-gray-500">Loading profiles...</div>;
  }

  const options = profiles.map(profile => ({
    value: profile.id,
    label: profile.name,
  }));

  return (
    <div className="flex items-center space-x-2">
      <span className="text-sm font-medium text-gray-700">Memory Profile:</span>
      <Dropdown
        options={options}
        value={currentProfile?.id || ''}
        onChange={handleChange}
        placeholder="Select a profile"
      />
      {currentProfile?.is_default && (
        <span className="text-xs text-blue-600">(Default)</span>
      )}
    </div>
  );
};

export default MemoryProfileSelector;

