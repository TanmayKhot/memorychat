/**
 * Main JavaScript file for MemoryChat Frontend
 * Handles API communication, UI updates, event handling, and state management
 */

// Application State
const AppState = {
    currentUserId: null,
    currentProfileId: null,
    currentSessionId: null,
    users: [],
    profiles: [],
    sessions: [],
    messages: [],
    connectionStatus: CONFIG.CONNECTION_STATUS.DISCONNECTED,
    theme: localStorage.getItem(CONFIG.STORAGE_KEYS.THEME) || CONFIG.THEME_LIGHT
};

// ============================================================================
// API CLIENT FUNCTIONS
// ============================================================================

/**
 * Make API request with error handling
 */
async function apiRequest(endpoint, options = {}) {
    const url = `${CONFIG.API_BASE_URL}${endpoint}`;
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
        },
        ...options
    };

    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), CONFIG.API_TIMEOUT);
        
        const response = await fetch(url, {
            ...defaultOptions,
            signal: controller.signal
        });
        
        clearTimeout(timeoutId);
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
            throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
        }
        
        return await response.json();
    } catch (error) {
        if (error.name === 'AbortError') {
            throw new Error('Request timeout');
        }
        throw error;
    }
}

/**
 * Health check
 */
async function checkApiHealth() {
    try {
        await apiRequest(CONFIG.ENDPOINTS.HEALTH);
        return true;
    } catch (error) {
        console.error('Health check failed:', error);
        return false;
    }
}

/**
 * User API functions
 */
const UserAPI = {
    async getAll() {
        return await apiRequest(CONFIG.ENDPOINTS.USERS);
    },
    
    async getById(id) {
        return await apiRequest(CONFIG.ENDPOINTS.USER_BY_ID(id));
    },
    
    async create(email, username) {
        return await apiRequest(CONFIG.ENDPOINTS.USERS, {
            method: 'POST',
            body: JSON.stringify({ email, username })
        });
    }
};

/**
 * Profile API functions
 */
const ProfileAPI = {
    async getByUserId(userId) {
        return await apiRequest(CONFIG.ENDPOINTS.USER_PROFILES(userId));
    },
    
    async getById(id) {
        return await apiRequest(CONFIG.ENDPOINTS.PROFILE_BY_ID(id));
    },
    
    async create(userId, name, description, systemPrompt) {
        return await apiRequest(CONFIG.ENDPOINTS.USER_PROFILES(userId), {
            method: 'POST',
            body: JSON.stringify({ name, description, system_prompt: systemPrompt })
        });
    },
    
    async update(id, name, description, systemPrompt, isDefault) {
        const body = {};
        if (name !== undefined) body.name = name;
        if (description !== undefined) body.description = description;
        if (systemPrompt !== undefined) body.system_prompt = systemPrompt;
        if (isDefault !== undefined) body.is_default = isDefault;
        
        return await apiRequest(CONFIG.ENDPOINTS.PROFILE_BY_ID(id), {
            method: 'PUT',
            body: JSON.stringify(body)
        });
    },
    
    async delete(id) {
        return await apiRequest(CONFIG.ENDPOINTS.PROFILE_BY_ID(id), {
            method: 'DELETE'
        });
    },
    
    async setDefault(id) {
        return await apiRequest(CONFIG.ENDPOINTS.SET_DEFAULT_PROFILE(id), {
            method: 'POST'
        });
    }
};

/**
 * Session API functions
 */
const SessionAPI = {
    async getByUserId(userId) {
        return await apiRequest(CONFIG.ENDPOINTS.USER_SESSIONS(userId));
    },
    
    async getById(id) {
        return await apiRequest(CONFIG.ENDPOINTS.SESSION_BY_ID(id));
    },
    
    async create(userId, profileId, privacyMode) {
        return await apiRequest(CONFIG.ENDPOINTS.USER_SESSIONS(userId), {
            method: 'POST',
            body: JSON.stringify({ memory_profile_id: profileId, privacy_mode: privacyMode })
        });
    },
    
    async updatePrivacyMode(id, privacyMode) {
        return await apiRequest(CONFIG.ENDPOINTS.SESSION_PRIVACY_MODE(id), {
            method: 'PUT',
            body: JSON.stringify({ privacy_mode: privacyMode })
        });
    },
    
    async delete(id) {
        return await apiRequest(CONFIG.ENDPOINTS.SESSION_BY_ID(id), {
            method: 'DELETE'
        });
    },
    
    async getMessages(id) {
        return await apiRequest(CONFIG.ENDPOINTS.SESSION_MESSAGES(id));
    }
};

/**
 * Chat API functions
 */
const ChatAPI = {
    async sendMessage(sessionId, message) {
        return await apiRequest(CONFIG.ENDPOINTS.SEND_MESSAGE, {
            method: 'POST',
            body: JSON.stringify({ session_id: sessionId, message })
        });
    }
};

// ============================================================================
// UI UPDATE FUNCTIONS
// ============================================================================

/**
 * Update connection status indicator
 */
function updateConnectionStatus(status) {
    AppState.connectionStatus = status;
    const statusDot = document.getElementById('statusDot');
    const statusText = document.getElementById('statusText');
    const apiStatus = document.getElementById('apiStatus');
    
    if (statusDot && statusText && apiStatus) {
        statusDot.className = 'w-2 h-2 rounded-full';
        statusText.textContent = CONFIG.STATUS_MESSAGES[status.toUpperCase()] || status;
        
        switch (status) {
            case CONFIG.CONNECTION_STATUS.CONNECTED:
                statusDot.classList.add('bg-green-500');
                apiStatus.textContent = 'API: Connected';
                apiStatus.className = 'text-green-500';
                break;
            case CONFIG.CONNECTION_STATUS.DISCONNECTED:
                statusDot.classList.add('bg-red-500');
                apiStatus.textContent = 'API: Disconnected';
                apiStatus.className = 'text-red-500';
                break;
            case CONFIG.CONNECTION_STATUS.CONNECTING:
                statusDot.classList.add('bg-yellow-500');
                apiStatus.textContent = 'API: Connecting...';
                apiStatus.className = 'text-yellow-500';
                break;
        }
    }
}

/**
 * Update user selector dropdown
 */
function updateUserSelector(users) {
    const selector = document.getElementById('userSelector');
    if (!selector) return;
    
    selector.innerHTML = '<option value="">Select User...</option>';
    users.forEach(user => {
        const option = document.createElement('option');
        option.value = user.id;
        option.textContent = `${user.username} (${user.email})`;
        if (user.id === AppState.currentUserId) {
            option.selected = true;
        }
        selector.appendChild(option);
    });
}

/**
 * Update profile selector dropdown
 */
function updateProfileSelector(profiles) {
    const selector = document.getElementById('profileSelector');
    const editBtn = document.getElementById('editProfileBtn');
    const deleteBtn = document.getElementById('deleteProfileBtn');
    
    if (!selector) return;
    
    selector.innerHTML = '<option value="">Select Profile...</option>';
    profiles.forEach(profile => {
        const option = document.createElement('option');
        option.value = profile.id;
        option.textContent = `${profile.name}${profile.is_default ? ' (Default)' : ''}`;
        if (profile.id === AppState.currentProfileId) {
            option.selected = true;
        }
        selector.appendChild(option);
    });
    
    // Show/hide edit and delete buttons based on selection
    if (AppState.currentProfileId && editBtn && deleteBtn) {
        editBtn.style.display = 'block';
        deleteBtn.style.display = 'block';
    } else if (editBtn && deleteBtn) {
        editBtn.style.display = 'none';
        deleteBtn.style.display = 'none';
    }
}

/**
 * Update session list
 */
function updateSessionList(sessions) {
    const container = document.getElementById('sessionList');
    if (!container) return;
    
    if (sessions.length === 0) {
        container.innerHTML = '<p class="text-sm text-gray-500 dark:text-gray-400 text-center py-4">No sessions yet</p>';
        return;
    }
    
    container.innerHTML = sessions.map(session => {
        const isActive = session.id === AppState.currentSessionId;
        const privacyClass = `privacy-${session.privacy_mode}`;
        return `
            <div class="session-item ${privacyClass} p-3 rounded-lg ${isActive ? 'bg-blue-100 dark:bg-blue-900' : 'bg-gray-50 dark:bg-gray-700'}" data-session-id="${session.id}">
                <div class="flex items-center justify-between">
                    <div class="flex-1 min-w-0 cursor-pointer" onclick="selectSession(${session.id})">
                        <p class="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
                            ${session.title || `Session ${session.id}`}
                        </p>
                        <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                            ${session.message_count} messages • ${formatDate(session.created_at)}
                        </p>
                    </div>
                    <div class="flex items-center space-x-1 ml-2">
                        ${isActive ? '<span class="text-blue-500 text-xs">●</span>' : ''}
                        <button class="delete-session-btn p-1 text-gray-400 hover:text-red-500 dark:hover:text-red-400 transition-colors" data-session-id="${session.id}" title="Delete Session" onclick="event.stopPropagation(); showDeleteConfirm('session', ${session.id}, '${escapeHtml(session.title || `Session ${session.id}`)}')">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                            </svg>
                        </button>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

/**
 * Update chat messages display
 */
function updateChatMessages(messages) {
    const container = document.getElementById('chatContainer');
    if (!container) return;
    
    if (messages.length === 0) {
        container.innerHTML = `
            <div class="text-center py-12">
                <div class="inline-block p-4 bg-blue-100 dark:bg-blue-900 rounded-full mb-4">
                    <svg class="w-12 h-12 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path>
                    </svg>
                </div>
                <h2 class="text-xl font-semibold text-gray-700 dark:text-gray-300 mb-2">Start a conversation</h2>
                <p class="text-gray-500 dark:text-gray-400">Send a message to begin chatting</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = messages.map(msg => {
        const isUser = msg.role === CONFIG.MESSAGE_ROLES.USER;
        return `
            <div class="message-bubble flex ${isUser ? 'justify-end' : 'justify-start'}">
                <div class="max-w-3xl ${isUser ? 'bg-blue-500 text-white' : 'bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100'} rounded-lg px-4 py-3 shadow-sm">
                    <p class="text-sm whitespace-pre-wrap">${escapeHtml(msg.content)}</p>
                    <p class="text-xs mt-1 ${isUser ? 'text-blue-100' : 'text-gray-500 dark:text-gray-400'}">
                        ${formatTime(msg.created_at)}
                        ${msg.agent_name ? ` • ${msg.agent_name}` : ''}
                    </p>
                </div>
            </div>
        `;
    }).join('');
    
    // Scroll to bottom
    container.scrollTop = container.scrollHeight;
}

/**
 * Update chat metadata display
 */
function updateChatMetadata(metadata = {}) {
    const memoriesUsed = document.getElementById('memoriesUsed');
    const newMemories = document.getElementById('newMemories');
    
    if (memoriesUsed) {
        memoriesUsed.textContent = `Memories: ${metadata.memories_used || 0}`;
    }
    if (newMemories) {
        newMemories.textContent = `New: ${metadata.new_memories_created || 0}`;
    }
}

/**
 * Update privacy mode description
 */
function updatePrivacyModeDescription(mode) {
    const description = document.getElementById('privacyModeDescription');
    if (description) {
        description.textContent = CONFIG.PRIVACY_MODE_DESCRIPTIONS[mode] || '';
    }
}

/**
 * Update input field state
 */
function updateInputState(enabled) {
    const input = document.getElementById('messageInput');
    const sendBtn = document.getElementById('sendBtn');
    
    if (input) {
        input.disabled = !enabled;
    }
    if (sendBtn) {
        sendBtn.disabled = !enabled;
    }
}

/**
 * Show/hide loading overlay
 */
function showLoading(show) {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        if (show) {
            overlay.classList.remove('hidden');
            overlay.classList.add('flex');
        } else {
            overlay.classList.add('hidden');
            overlay.classList.remove('flex');
        }
    }
}

/**
 * Show error message
 */
function showError(message) {
    const warnings = document.getElementById('inputWarnings');
    if (warnings) {
        warnings.innerHTML = `<div class="error-message">${escapeHtml(message)}</div>`;
        setTimeout(() => {
            warnings.innerHTML = '';
        }, 5000);
    }
}

/**
 * Show warning message
 */
function showWarning(message) {
    const warnings = document.getElementById('inputWarnings');
    if (warnings) {
        warnings.innerHTML = `<div class="warning-message">${escapeHtml(message)}</div>`;
    }
}

// ============================================================================
// STATE MANAGEMENT FUNCTIONS
// ============================================================================

/**
 * Load initial state from localStorage
 */
function loadState() {
    const savedUserId = localStorage.getItem(CONFIG.STORAGE_KEYS.CURRENT_USER_ID);
    const savedProfileId = localStorage.getItem(CONFIG.STORAGE_KEYS.CURRENT_PROFILE_ID);
    const savedSessionId = localStorage.getItem(CONFIG.STORAGE_KEYS.CURRENT_SESSION_ID);
    
    if (savedUserId) AppState.currentUserId = parseInt(savedUserId);
    if (savedProfileId) AppState.currentProfileId = parseInt(savedProfileId);
    if (savedSessionId) AppState.currentSessionId = parseInt(savedSessionId);
}

/**
 * Save state to localStorage
 */
function saveState() {
    if (AppState.currentUserId) {
        localStorage.setItem(CONFIG.STORAGE_KEYS.CURRENT_USER_ID, AppState.currentUserId);
    }
    if (AppState.currentProfileId) {
        localStorage.setItem(CONFIG.STORAGE_KEYS.CURRENT_PROFILE_ID, AppState.currentProfileId);
    }
    if (AppState.currentSessionId) {
        localStorage.setItem(CONFIG.STORAGE_KEYS.CURRENT_SESSION_ID, AppState.currentSessionId);
    }
}

/**
 * Select user
 */
async function selectUser(userId) {
    AppState.currentUserId = userId;
    AppState.currentProfileId = null;
    AppState.currentSessionId = null;
    saveState();
    
    updateInputState(false);
    updateChatMessages([]);
    
    if (userId) {
        await loadProfiles();
        await loadSessions();
    } else {
        updateProfileSelector([]);
        updateSessionList([]);
    }
}

/**
 * Select profile
 */
async function selectProfile(profileId) {
    AppState.currentProfileId = profileId;
    AppState.currentSessionId = null;
    saveState();
    
    updateInputState(false);
    updateChatMessages([]);
    
    if (profileId) {
        await loadSessions();
    } else {
        updateSessionList([]);
    }
}

/**
 * Select session
 */
async function selectSession(sessionId) {
    AppState.currentSessionId = sessionId;
    saveState();
    
    if (sessionId) {
        await loadMessages();
        updateInputState(true);
        updateSessionInfo();
    } else {
        updateChatMessages([]);
        updateInputState(false);
    }
}

/**
 * Load users
 */
async function loadUsers() {
    try {
        const users = await UserAPI.getAll();
        AppState.users = users;
        updateUserSelector(users);
        
        // Auto-select if only one user or if saved user exists
        if (users.length === 1) {
            await selectUser(users[0].id);
        } else if (AppState.currentUserId && users.find(u => u.id === AppState.currentUserId)) {
            await selectUser(AppState.currentUserId);
        }
    } catch (error) {
        console.error('Failed to load users:', error);
        showError('Failed to load users');
    }
}

/**
 * Load profiles
 */
async function loadProfiles() {
    if (!AppState.currentUserId) return;
    
    try {
        const profiles = await ProfileAPI.getByUserId(AppState.currentUserId);
        AppState.profiles = profiles;
        updateProfileSelector(profiles);
        
        // Auto-select default profile if available
        const defaultProfile = profiles.find(p => p.is_default);
        if (defaultProfile && !AppState.currentProfileId) {
            await selectProfile(defaultProfile.id);
        } else if (AppState.currentProfileId && profiles.find(p => p.id === AppState.currentProfileId)) {
            await selectProfile(AppState.currentProfileId);
        }
    } catch (error) {
        console.error('Failed to load profiles:', error);
        showError('Failed to load profiles');
    }
}

/**
 * Load sessions
 */
async function loadSessions() {
    if (!AppState.currentUserId) return;
    
    try {
        const sessions = await SessionAPI.getByUserId(AppState.currentUserId);
        AppState.sessions = sessions;
        updateSessionList(sessions);
        
        // Auto-select session if saved session exists
        if (AppState.currentSessionId && sessions.find(s => s.id === AppState.currentSessionId)) {
            await selectSession(AppState.currentSessionId);
        }
    } catch (error) {
        console.error('Failed to load sessions:', error);
        showError('Failed to load sessions');
    }
}

/**
 * Load messages
 */
async function loadMessages() {
    if (!AppState.currentSessionId) return;
    
    try {
        const messages = await SessionAPI.getMessages(AppState.currentSessionId);
        AppState.messages = messages;
        updateChatMessages(messages);
    } catch (error) {
        console.error('Failed to load messages:', error);
        showError('Failed to load messages');
    }
}

/**
 * Update session info in footer
 */
function updateSessionInfo() {
    const info = document.getElementById('currentSessionInfo');
    if (info && AppState.currentSessionId) {
        const session = AppState.sessions.find(s => s.id === AppState.currentSessionId);
        if (session) {
            info.textContent = `Session: ${session.title || session.id}`;
        }
    }
}

// ============================================================================
// EVENT HANDLERS
// ============================================================================

/**
 * Handle send message
 */
async function handleSendMessage() {
    const input = document.getElementById('messageInput');
    const message = input?.value.trim();
    
    if (!message || !AppState.currentSessionId) return;
    
    // Add user message to UI immediately
    const userMessage = {
        id: Date.now(),
        role: CONFIG.MESSAGE_ROLES.USER,
        content: message,
        created_at: new Date().toISOString()
    };
    AppState.messages.push(userMessage);
    updateChatMessages(AppState.messages);
    
    // Clear input
    input.value = '';
    
    // Show loading
    showLoading(true);
    updateInputState(false);
    
    try {
        const response = await ChatAPI.sendMessage(AppState.currentSessionId, message);
        
        // Add assistant response
        const assistantMessage = {
            id: Date.now() + 1,
            role: CONFIG.MESSAGE_ROLES.ASSISTANT,
            content: response.message,
            created_at: new Date().toISOString(),
            agent_name: 'Assistant'
        };
        AppState.messages.push(assistantMessage);
        updateChatMessages(AppState.messages);
        
        // Update metadata
        updateChatMetadata({
            memories_used: response.memories_used,
            new_memories_created: response.new_memories_created
        });
        
        // Show warnings if any
        if (response.warnings && response.warnings.length > 0) {
            response.warnings.forEach(warning => showWarning(warning));
        }
        
        // Reload messages to get server-side data
        await loadMessages();
        
        // Reload sessions to update message count
        await loadSessions();
        
    } catch (error) {
        console.error('Failed to send message:', error);
        showError(error.message || 'Failed to send message');
        
        // Remove user message on error
        AppState.messages = AppState.messages.filter(m => m.id !== userMessage.id);
        updateChatMessages(AppState.messages);
    } finally {
        showLoading(false);
        updateInputState(true);
        input?.focus();
    }
}

/**
 * Handle create user
 */
async function handleCreateUser(event) {
    event.preventDefault();
    
    const email = document.getElementById('userEmail')?.value.trim();
    const username = document.getElementById('userUsername')?.value.trim();
    
    if (!email || !username) {
        showError('Email and username are required');
        return;
    }
    
    showLoading(true);
    
    try {
        const user = await UserAPI.create(email, username);
        await loadUsers();
        await selectUser(user.id);
        
        // Close modal
        document.getElementById('createUserModal')?.classList.add('hidden');
        document.getElementById('createUserForm')?.reset();
    } catch (error) {
        console.error('Failed to create user:', error);
        showError(error.message || 'Failed to create user');
    } finally {
        showLoading(false);
    }
}

/**
 * Handle create profile
 */
async function handleCreateProfile(event) {
    event.preventDefault();
    
    if (!AppState.currentUserId) {
        showError('Please select a user first');
        return;
    }
    
    const name = document.getElementById('profileName')?.value.trim();
    const description = document.getElementById('profileDescription')?.value.trim() || null;
    const systemPrompt = document.getElementById('profileSystemPrompt')?.value.trim() || null;
    
    if (!name) {
        showError('Profile name is required');
        return;
    }
    
    showLoading(true);
    
    try {
        const profile = await ProfileAPI.create(AppState.currentUserId, name, description, systemPrompt);
        await loadProfiles();
        await selectProfile(profile.id);
        
        // Close modal
        document.getElementById('createProfileModal')?.classList.add('hidden');
        document.getElementById('createProfileForm')?.reset();
    } catch (error) {
        console.error('Failed to create profile:', error);
        showError(error.message || 'Failed to create profile');
    } finally {
        showLoading(false);
    }
}

/**
 * Handle create session
 */
async function handleCreateSession() {
    if (!AppState.currentUserId || !AppState.currentProfileId) {
        showError('Please select a user and profile first');
        return;
    }
    
    const privacyMode = document.getElementById('privacyModeSelector')?.value || CONFIG.PRIVACY_MODES.NORMAL;
    
    showLoading(true);
    
    try {
        const session = await SessionAPI.create(AppState.currentUserId, AppState.currentProfileId, privacyMode);
        await loadSessions();
        await selectSession(session.id);
    } catch (error) {
        console.error('Failed to create session:', error);
        showError(error.message || 'Failed to create session');
    } finally {
        showLoading(false);
    }
}

/**
 * Handle privacy mode change
 */
async function handlePrivacyModeChange() {
    if (!AppState.currentSessionId) return;
    
    const privacyMode = document.getElementById('privacyModeSelector')?.value;
    if (!privacyMode) return;
    
    showLoading(true);
    
    try {
        await SessionAPI.updatePrivacyMode(AppState.currentSessionId, privacyMode);
        await loadSessions();
        updatePrivacyModeDescription(privacyMode);
    } catch (error) {
        console.error('Failed to update privacy mode:', error);
        showError(error.message || 'Failed to update privacy mode');
    } finally {
        showLoading(false);
    }
}

/**
 * Toggle theme
 */
function toggleTheme() {
    const html = document.documentElement;
    if (AppState.theme === CONFIG.THEME_DARK) {
        AppState.theme = CONFIG.THEME_LIGHT;
        html.classList.remove('dark');
    } else {
        AppState.theme = CONFIG.THEME_DARK;
        html.classList.add('dark');
    }
    localStorage.setItem(CONFIG.STORAGE_KEYS.THEME, AppState.theme);
    updateThemeIcon();
}

/**
 * Update theme icon
 */
function updateThemeIcon() {
    const icon = document.getElementById('themeIcon');
    if (!icon) return;
    
    if (AppState.theme === CONFIG.THEME_DARK) {
        icon.innerHTML = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"></path>';
    } else {
        icon.innerHTML = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"></path>';
    }
}

/**
 * Show delete confirmation modal
 */
let pendingDeleteAction = null;

function showDeleteConfirm(type, id, name) {
    const modal = document.getElementById('confirmDeleteModal');
    const title = document.getElementById('deleteModalTitle');
    const message = document.getElementById('deleteModalMessage');
    
    if (!modal || !title || !message) return;
    
    title.textContent = `Delete ${type.charAt(0).toUpperCase() + type.slice(1)}`;
    message.textContent = `Are you sure you want to delete "${name}"? This action cannot be undone.`;
    
    pendingDeleteAction = { type, id, name };
    
    modal.classList.remove('hidden');
    modal.classList.add('flex');
}

/**
 * Handle confirmed delete
 */
async function handleConfirmedDelete() {
    if (!pendingDeleteAction) return;
    
    const { type, id } = pendingDeleteAction;
    showLoading(true);
    
    try {
        if (type === 'profile') {
            await ProfileAPI.delete(id);
            if (AppState.currentProfileId === id) {
                AppState.currentProfileId = null;
                AppState.currentSessionId = null;
                saveState();
            }
            await loadProfiles();
            await loadSessions();
        } else if (type === 'session') {
            await SessionAPI.delete(id);
            if (AppState.currentSessionId === id) {
                AppState.currentSessionId = null;
                saveState();
                updateChatMessages([]);
                updateInputState(false);
            }
            await loadSessions();
        }
        
        // Close modal
        document.getElementById('confirmDeleteModal')?.classList.add('hidden');
        document.getElementById('confirmDeleteModal')?.classList.remove('flex');
        pendingDeleteAction = null;
    } catch (error) {
        console.error(`Failed to delete ${type}:`, error);
        showError(error.message || `Failed to delete ${type}`);
    } finally {
        showLoading(false);
    }
}

/**
 * Handle edit profile
 */
async function handleEditProfile() {
    if (!AppState.currentProfileId) {
        showError('Please select a profile to edit');
        return;
    }
    
    showLoading(true);
    
    try {
        const profile = await ProfileAPI.getById(AppState.currentProfileId);
        
        // Populate edit form
        document.getElementById('editProfileId').value = profile.id;
        document.getElementById('editProfileName').value = profile.name || '';
        document.getElementById('editProfileDescription').value = profile.description || '';
        document.getElementById('editProfileSystemPrompt').value = profile.system_prompt || '';
        document.getElementById('editProfileIsDefault').checked = profile.is_default || false;
        
        // Show settings modal
        document.getElementById('settingsModal')?.classList.remove('hidden');
        document.getElementById('settingsModal')?.classList.add('flex');
    } catch (error) {
        console.error('Failed to load profile for editing:', error);
        showError(error.message || 'Failed to load profile');
    } finally {
        showLoading(false);
    }
}

/**
 * Handle save edited profile
 */
async function handleSaveEditedProfile(event) {
    event.preventDefault();
    
    const id = parseInt(document.getElementById('editProfileId')?.value);
    const name = document.getElementById('editProfileName')?.value.trim();
    const description = document.getElementById('editProfileDescription')?.value.trim() || null;
    const systemPrompt = document.getElementById('editProfileSystemPrompt')?.value.trim() || null;
    const isDefault = document.getElementById('editProfileIsDefault')?.checked;
    
    if (!id || !name) {
        showError('Profile name is required');
        return;
    }
    
    showLoading(true);
    
    try {
        await ProfileAPI.update(id, name, description, systemPrompt, isDefault);
        await loadProfiles();
        
        // Close settings modal
        document.getElementById('settingsModal')?.classList.add('hidden');
        document.getElementById('settingsModal')?.classList.remove('flex');
    } catch (error) {
        console.error('Failed to update profile:', error);
        showError(error.message || 'Failed to update profile');
    } finally {
        showLoading(false);
    }
}

/**
 * Handle save settings
 */
function handleSaveSettings() {
    const apiUrl = document.getElementById('settingsApiUrl')?.value.trim();
    const autoSave = document.getElementById('settingsAutoSave')?.checked;
    const showMetadata = document.getElementById('settingsShowMetadata')?.checked;
    
    if (apiUrl && apiUrl !== CONFIG.API_BASE_URL) {
        CONFIG.API_BASE_URL = apiUrl;
        localStorage.setItem('memorychat-api-url', apiUrl);
        showWarning('API URL changed. Page will reload.');
        setTimeout(() => location.reload(), 1000);
        return;
    }
    
    localStorage.setItem('memorychat-auto-save', autoSave);
    localStorage.setItem('memorychat-show-metadata', showMetadata);
    
    // Update metadata visibility
    const metadataDiv = document.getElementById('chatMetadata');
    if (metadataDiv) {
        metadataDiv.style.display = showMetadata ? 'flex' : 'none';
    }
    
    // Close settings modal
    document.getElementById('settingsModal')?.classList.add('hidden');
    document.getElementById('settingsModal')?.classList.remove('flex');
}

/**
 * Load settings
 */
function loadSettings() {
    const savedApiUrl = localStorage.getItem('memorychat-api-url');
    const autoSave = localStorage.getItem('memorychat-auto-save');
    const showMetadata = localStorage.getItem('memorychat-show-metadata');
    
    if (savedApiUrl) {
        CONFIG.API_BASE_URL = savedApiUrl;
        const apiUrlInput = document.getElementById('settingsApiUrl');
        if (apiUrlInput) apiUrlInput.value = savedApiUrl;
    }
    
    const autoSaveCheckbox = document.getElementById('settingsAutoSave');
    if (autoSaveCheckbox) {
        autoSaveCheckbox.checked = autoSave !== 'false';
    }
    
    const showMetadataCheckbox = document.getElementById('settingsShowMetadata');
    if (showMetadataCheckbox) {
        showMetadataCheckbox.checked = showMetadata !== 'false';
        const metadataDiv = document.getElementById('chatMetadata');
        if (metadataDiv) {
            metadataDiv.style.display = showMetadataCheckbox.checked ? 'flex' : 'none';
        }
    }
}

/**
 * Update theme icon
 */
function updateThemeIcon() {
    const icon = document.getElementById('themeIcon');
    if (!icon) return;
    
    if (AppState.theme === CONFIG.THEME_DARK) {
        icon.innerHTML = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"></path>';
    } else {
        icon.innerHTML = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"></path>';
    }
}

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Format date
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    
    if (days === 0) return 'Today';
    if (days === 1) return 'Yesterday';
    if (days < 7) return `${days} days ago`;
    
    return date.toLocaleDateString();
}

/**
 * Format time
 */
function formatTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

// ============================================================================
// INITIALIZATION
// ============================================================================

/**
 * Initialize application
 */
async function init() {
    // Load saved state
    loadState();
    
    // Apply theme
    if (AppState.theme === CONFIG.THEME_DARK) {
        document.documentElement.classList.add('dark');
    }
    updateThemeIcon();
    
    // Check API connection
    updateConnectionStatus(CONFIG.CONNECTION_STATUS.CONNECTING);
    const isHealthy = await checkApiHealth();
    updateConnectionStatus(isHealthy ? CONFIG.CONNECTION_STATUS.CONNECTED : CONFIG.CONNECTION_STATUS.DISCONNECTED);
    
    // Load settings
    loadSettings();
    
    // Load initial data
    await loadUsers();
    
    // Set up event listeners
    setupEventListeners();
    
    // Set up periodic health check
    setInterval(async () => {
        const isHealthy = await checkApiHealth();
        updateConnectionStatus(isHealthy ? CONFIG.CONNECTION_STATUS.CONNECTED : CONFIG.CONNECTION_STATUS.DISCONNECTED);
    }, 30000); // Check every 30 seconds
}

/**
 * Set up event listeners
 */
function setupEventListeners() {
    // User selector
    document.getElementById('userSelector')?.addEventListener('change', (e) => {
        const userId = e.target.value ? parseInt(e.target.value) : null;
        selectUser(userId);
    });
    
    // Profile selector
    document.getElementById('profileSelector')?.addEventListener('change', (e) => {
        const profileId = e.target.value ? parseInt(e.target.value) : null;
        selectProfile(profileId);
    });
    
    // Edit profile button
    document.getElementById('editProfileBtn')?.addEventListener('click', handleEditProfile);
    
    // Delete profile button
    document.getElementById('deleteProfileBtn')?.addEventListener('click', () => {
        if (!AppState.currentProfileId) return;
        const profile = AppState.profiles.find(p => p.id === AppState.currentProfileId);
        if (profile) {
            showDeleteConfirm('profile', profile.id, profile.name);
        }
    });
    
    // Privacy mode selector
    document.getElementById('privacyModeSelector')?.addEventListener('change', (e) => {
        updatePrivacyModeDescription(e.target.value);
        if (AppState.currentSessionId) {
            handlePrivacyModeChange();
        }
    });
    
    // Send button
    document.getElementById('sendBtn')?.addEventListener('click', handleSendMessage);
    
    // Message input - Enter to send, Shift+Enter for new line
    document.getElementById('messageInput')?.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    });
    
    // Auto-resize textarea
    document.getElementById('messageInput')?.addEventListener('input', (e) => {
        e.target.style.height = 'auto';
        e.target.style.height = `${Math.min(e.target.scrollHeight, 200)}px`;
    });
    
    // Create user button
    document.getElementById('createUserBtn')?.addEventListener('click', () => {
        document.getElementById('createUserModal')?.classList.remove('hidden');
        document.getElementById('createUserModal')?.classList.add('flex');
    });
    
    // Cancel user button
    document.getElementById('cancelUserBtn')?.addEventListener('click', () => {
        document.getElementById('createUserModal')?.classList.add('hidden');
        document.getElementById('createUserModal')?.classList.remove('flex');
        document.getElementById('createUserForm')?.reset();
    });
    
    // Create user form
    document.getElementById('createUserForm')?.addEventListener('submit', handleCreateUser);
    
    // Create profile button
    document.getElementById('createProfileBtn')?.addEventListener('click', () => {
        if (!AppState.currentUserId) {
            showError('Please select a user first');
            return;
        }
        document.getElementById('createProfileModal')?.classList.remove('hidden');
        document.getElementById('createProfileModal')?.classList.add('flex');
    });
    
    // Cancel profile button
    document.getElementById('cancelProfileBtn')?.addEventListener('click', () => {
        document.getElementById('createProfileModal')?.classList.add('hidden');
        document.getElementById('createProfileModal')?.classList.remove('flex');
        document.getElementById('createProfileForm')?.reset();
    });
    
    // Create profile form
    document.getElementById('createProfileForm')?.addEventListener('submit', handleCreateProfile);
    
    // New session button
    document.getElementById('newSessionBtn')?.addEventListener('click', handleCreateSession);
    
    // Theme toggle
    document.getElementById('themeToggle')?.addEventListener('click', toggleTheme);
    
    // Settings button
    document.getElementById('settingsBtn')?.addEventListener('click', () => {
        // Load current profile if selected
        if (AppState.currentProfileId) {
            handleEditProfile();
        } else {
            document.getElementById('settingsModal')?.classList.remove('hidden');
            document.getElementById('settingsModal')?.classList.add('flex');
        }
    });
    
    // Close settings button
    document.getElementById('closeSettingsBtn')?.addEventListener('click', () => {
        document.getElementById('settingsModal')?.classList.add('hidden');
        document.getElementById('settingsModal')?.classList.remove('flex');
    });
    
    // Cancel edit profile
    document.getElementById('cancelEditProfileBtn')?.addEventListener('click', () => {
        document.getElementById('settingsModal')?.classList.add('hidden');
        document.getElementById('settingsModal')?.classList.remove('flex');
    });
    
    // Edit profile form
    document.getElementById('editProfileForm')?.addEventListener('submit', handleSaveEditedProfile);
    
    // Save settings button
    document.getElementById('saveSettingsBtn')?.addEventListener('click', handleSaveSettings);
    
    // Confirm delete button
    document.getElementById('confirmDeleteBtn')?.addEventListener('click', handleConfirmedDelete);
    
    // Cancel delete button
    document.getElementById('cancelDeleteBtn')?.addEventListener('click', () => {
        document.getElementById('confirmDeleteModal')?.classList.add('hidden');
        document.getElementById('confirmDeleteModal')?.classList.remove('flex');
        pendingDeleteAction = null;
    });
    
    // Close modals on backdrop click
    document.getElementById('createUserModal')?.addEventListener('click', (e) => {
        if (e.target.id === 'createUserModal') {
            e.target.classList.add('hidden');
            e.target.classList.remove('flex');
        }
    });
    
    document.getElementById('createProfileModal')?.addEventListener('click', (e) => {
        if (e.target.id === 'createProfileModal') {
            e.target.classList.add('hidden');
            e.target.classList.remove('flex');
        }
    });
    
    document.getElementById('confirmDeleteModal')?.addEventListener('click', (e) => {
        if (e.target.id === 'confirmDeleteModal') {
            e.target.classList.add('hidden');
            e.target.classList.remove('flex');
            pendingDeleteAction = null;
        }
    });
    
    document.getElementById('settingsModal')?.addEventListener('click', (e) => {
        if (e.target.id === 'settingsModal') {
            e.target.classList.add('hidden');
            e.target.classList.remove('flex');
        }
    });
}

// Make selectSession available globally for onclick handlers
window.selectSession = selectSession;
window.showDeleteConfirm = showDeleteConfirm;

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}

