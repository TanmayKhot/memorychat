/**
 * Configuration file for MemoryChat Frontend
 * Contains API base URL and application constants
 */

const CONFIG = {
    // API Configuration
    API_BASE_URL: 'http://127.0.0.1:8000',
    API_TIMEOUT: 30000, // 30 seconds
    
    // API Endpoints
    ENDPOINTS: {
        // Health check
        HEALTH: '/health',
        
        // Users
        USERS: '/api/users',
        USER_BY_ID: (id) => `/api/users/${id}`,
        
        // Memory Profiles
        USER_PROFILES: (userId) => `/api/users/${userId}/profiles`,
        PROFILE_BY_ID: (id) => `/api/profiles/${id}`,
        SET_DEFAULT_PROFILE: (id) => `/api/profiles/${id}/set-default`,
        
        // Sessions
        USER_SESSIONS: (userId) => `/api/users/${userId}/sessions`,
        SESSION_BY_ID: (id) => `/api/sessions/${id}`,
        SESSION_PRIVACY_MODE: (id) => `/api/sessions/${id}/privacy-mode`,
        SESSION_MESSAGES: (id) => `/api/sessions/${id}/messages`,
        SESSION_CONTEXT: (id) => `/api/sessions/${id}/context`,
        
        // Chat
        SEND_MESSAGE: '/api/chat/message',
        
        // Memories
        PROFILE_MEMORIES: (profileId) => `/api/profiles/${profileId}/memories`,
        MEMORY_BY_ID: (id) => `/api/memories/${id}`,
        SEARCH_MEMORIES: '/api/memories/search',
        
        // Analytics
        SESSION_ANALYTICS: (id) => `/api/sessions/${id}/analytics`,
        PROFILE_ANALYTICS: (id) => `/api/profiles/${id}/analytics`,
    },
    
    // Privacy Modes
    PRIVACY_MODES: {
        NORMAL: 'normal',
        INCOGNITO: 'incognito',
        PAUSE_MEMORY: 'pause_memory'
    },
    
    // Privacy Mode Descriptions
    PRIVACY_MODE_DESCRIPTIONS: {
        normal: 'Normal: Full memory storage and retrieval',
        incognito: 'Incognito: No memory storage or retrieval',
        pause_memory: 'Pause Memory: Memory retrieval only, no new storage'
    },
    
    // Message Roles
    MESSAGE_ROLES: {
        USER: 'user',
        ASSISTANT: 'assistant',
        SYSTEM: 'system'
    },
    
    // Memory Types
    MEMORY_TYPES: {
        FACT: 'fact',
        PREFERENCE: 'preference',
        EVENT: 'event',
        RELATIONSHIP: 'relationship',
        OTHER: 'other'
    },
    
    // UI Constants
    MAX_MESSAGE_LENGTH: 10000,
    MESSAGES_PER_PAGE: 50,
    SESSIONS_PER_PAGE: 20,
    
    // Theme
    THEME_STORAGE_KEY: 'memorychat-theme',
    THEME_DARK: 'dark',
    THEME_LIGHT: 'light',
    
    // Local Storage Keys
    STORAGE_KEYS: {
        CURRENT_USER_ID: 'memorychat-current-user-id',
        CURRENT_PROFILE_ID: 'memorychat-current-profile-id',
        CURRENT_SESSION_ID: 'memorychat-current-session-id',
        THEME: 'memorychat-theme'
    },
    
    // Connection Status
    CONNECTION_STATUS: {
        CONNECTED: 'connected',
        DISCONNECTED: 'disconnected',
        CONNECTING: 'connecting'
    },
    
    // Status Messages
    STATUS_MESSAGES: {
        CONNECTED: 'Connected',
        DISCONNECTED: 'Disconnected',
        CONNECTING: 'Connecting...'
    }
};

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CONFIG;
}

