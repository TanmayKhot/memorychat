import { useState, useEffect } from 'react';
import { useMemoryProfiles } from '../../hooks/useMemoryProfiles';
import Modal from '../ui/Modal';
import Input from '../ui/Input';
import Button from '../ui/Button';
import type { MemoryProfile } from '../../types';

interface CreateMemoryProfileModalProps {
  profile?: MemoryProfile;
  onClose: () => void;
}

const CreateMemoryProfileModal = ({ profile, onClose }: CreateMemoryProfileModalProps) => {
  const [name, setName] = useState(profile?.name || '');
  const [description, setDescription] = useState(profile?.description || '');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { createProfile, updateProfile } = useMemoryProfiles();

  useEffect(() => {
    if (profile) {
      setName(profile.name);
      setDescription(profile.description || '');
    }
  }, [profile]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!name.trim()) {
      setError('Profile name is required');
      return;
    }

    setLoading(true);

    try {
      if (profile) {
        await updateProfile(profile.id, { name, description });
      } else {
        await createProfile({ name, description });
      }
      onClose();
    } catch (err: any) {
      setError(err.message || 'Failed to save profile');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal
      isOpen={true}
      onClose={onClose}
      title={profile ? 'Edit Memory Profile' : 'Create Memory Profile'}
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="name" className="block text-sm font-medium text-gray-700">
            Profile Name *
          </label>
          <Input
            id="name"
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="e.g., Work, Personal, Study"
            required
            disabled={loading}
          />
        </div>

        <div>
          <label htmlFor="description" className="block text-sm font-medium text-gray-700">
            Description (Optional)
          </label>
          <textarea
            id="description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Brief description of this memory profile"
            disabled={loading}
            rows={3}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
          />
        </div>

        {error && (
          <div className="text-red-600 text-sm">
            {error}
          </div>
        )}

        <div className="flex justify-end space-x-2">
          <Button
            type="button"
            onClick={onClose}
            variant="outline"
            disabled={loading}
          >
            Cancel
          </Button>
          <Button type="submit" disabled={loading}>
            {loading ? 'Saving...' : profile ? 'Update' : 'Create'}
          </Button>
        </div>
      </form>
    </Modal>
  );
};

export default CreateMemoryProfileModal;

