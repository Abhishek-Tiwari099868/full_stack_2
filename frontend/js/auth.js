/**
 * Authentication service handling api communication, token storage, and session state.
 */
const authService = {
    /**
     * Authenticate user and retrieve JWT token.
     * @param {string} email 
     * @param {string} password 
     */
    async login(email, password) {
        const data = await apiRequest('/auth/login', {
            method: 'POST',
            body: { email, password }
        });

        if (data.success && data.access_token) {
            localStorage.setItem('token', data.access_token);
        }
        return data;
    },

    /**
     * Register a new user account.
     * @param {string} name 
     * @param {string} email 
     * @param {string} password 
     */
    async register(name, email, password) {
        return await apiRequest('/auth/register', {
            method: 'POST',
            body: { name, email, password }
        });
    },

    /**
     * Restore user session by verifying the stored token.
     */
    async restoreSession() {
        const token = localStorage.getItem('token');
        if (!token) return;

        try {
            const data = await apiRequest('/auth/profile');
            if (data.success && data.user) {
                if (window.authState) {
                    window.authState.isLoggedIn = true;
                    window.authState.performLogin(data.user.name, data.user.email);
                }
            } else {
                localStorage.removeItem('token');
            }
        } catch (err) {
            console.error('Failed to restore session:', err);
            localStorage.removeItem('token');
        }
    },

    /**
     * Clear token and trigger logout UI.
     */
    logout() {
        if (window.authState) {
            window.authState.performLogout();
        } else {
            localStorage.removeItem('token');
        }
    }
};

// Parse query parameters to extract token from URL redirection (OAuth callbacks)
const urlParams = new URLSearchParams(window.location.search);
const urlToken = urlParams.get('token');
if (urlToken) {
    localStorage.setItem('token', urlToken);
    
    // Clean URL query parameters
    urlParams.delete('token');
    const newQuery = urlParams.toString();
    const cleanUrl = window.location.pathname + (newQuery ? '?' + newQuery : '') + window.location.hash;
    window.history.replaceState({}, document.title, cleanUrl);
}

// Auto-restore session immediately since window.authState is defined in the preceding script tag
authService.restoreSession();
