import { useState } from 'react';
import { useMemoryProfiles } from '../../hooks/useMemoryProfiles';
import Button from '../ui/Button';
import CreateMemoryProfileModal from './CreateMemoryProfileModal';
import type { MemoryProfile } from '../../types';

const MemoryProfileManager = () => {
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [editingProfile, setEditingProfile] = useState<MemoryProfile | null>(null);
  const { profiles, deleteProfile, setDefaultProfile, isLoading } = useMemoryProfiles();

  const handleDelete = async (profileId: string) => {
    if (profiles.length <= 1) {
      alert('Cannot delete the only profile');
      return;
    }

    const confirmed = window.confirm(
      'Are you sure you want to delete this profile? All associated memories will be deleted.'
    );

    if (confirmed) {
      await deleteProfile(profileId);
    }
  };

  const handleSetDefault = async (profileId: string) => {
    await setDefaultProfile(profileId);
  };

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Memory Profiles</h2>
        <Button onClick={() => setShowCreateModal(true)}>
          + New Profile
        </Button>
      </div>

      {isLoading ? (
        <div className="text-gray-500">Loading profiles...</div>
      ) : (
        <div className="space-y-3">
          {profiles.map((profile) => (
            <div
              key={profile.id}
              className="border border-gray-300 rounded-lg p-4 hover:bg-gray-50"
            >
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="flex items-center space-x-2">
                    <h3 className="font-semibold text-lg">{profile.name}</h3>
                    {profile.is_default && (
                      <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">
                        Default
                      </span>
                    )}
                  </div>
                  {profile.description && (
                    <p className="text-gray-600 text-sm mt-1">{profile.description}</p>
                  )}
                  <p className="text-xs text-gray-500 mt-2">
                    Created: {new Date(profile.created_at).toLocaleDateString()}
                  </p>
                </div>
                
                <div className="flex space-x-2">
                  {!profile.is_default && (
                    <Button
                      onClick={() => handleSetDefault(profile.id)}
                      variant="outline"
                      size="sm"
                    >
                      Set Default
                    </Button>
                  )}
                  <Button
                    onClick={() => setEditingProfile(profile)}
                    variant="outline"
                    size="sm"
                  >
                    Edit
                  </Button>
                  <Button
                    onClick={() => handleDelete(profile.id)}
                    variant="danger"
                    size="sm"
                    disabled={profiles.length <= 1}
                  >
                    Delete
                  </Button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {showCreateModal && (
        <CreateMemoryProfileModal
          onClose={() => setShowCreateModal(false)}
        />
      )}

      {editingProfile && (
        <CreateMemoryProfileModal
          profile={editingProfile}
          onClose={() => setEditingProfile(null)}
        />
      )}
    </div>
  );
};

export default MemoryProfileManager;

