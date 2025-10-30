import Layout from '../components/layout/Layout';
import MemoryProfileManager from '../components/memory/MemoryProfileManager';

const Settings = () => {
  return (
    <Layout showSidebar={false}>
      <div className="h-full overflow-y-auto bg-gray-50">
        <div className="max-w-4xl mx-auto py-8 px-4">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
            <p className="text-gray-600 mt-2">
              Manage your memory profiles and account settings
            </p>
          </div>

          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <MemoryProfileManager />
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Account Settings</h2>
            <div className="space-y-4">
              <div>
                <h3 className="text-sm font-medium text-gray-700">Privacy</h3>
                <p className="text-sm text-gray-600 mt-1">
                  Your data is private and secure. Only you have access to your memories and conversations.
                </p>
              </div>
              
              <div>
                <h3 className="text-sm font-medium text-gray-700">Data Export</h3>
                <p className="text-sm text-gray-600 mt-1">
                  You can export your data at any time. (Feature coming soon)
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default Settings;

