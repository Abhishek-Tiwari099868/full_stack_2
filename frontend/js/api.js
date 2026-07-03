const API_BASE_URL = (window.BACKEND_URL || 'http://127.0.0.1:5000') + '/api';

/**
 * Common API request helper.
 * @param {string} endpoint - API path (e.g. '/auth/login')
 * @param {object} options - Fetch options (method, headers, body, etc.)
 * @returns {Promise<object>} Parsed JSON response
 */
async function apiRequest(endpoint, options = {}) {
    const token = localStorage.getItem('token');
    
    // Setup headers
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };
    
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    // Prepare body
    let body = options.body;
    if (body && typeof body === 'object') {
        body = JSON.stringify(body);
    }

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...options,
        headers,
        body
    });

    const data = await response.json().catch(() => ({
        success: false,
        message: 'Invalid JSON response from server'
    }));

    if (!response.ok) {
        // Build readable error message from response data
        const errMsg = data.message || (data.errors ? Object.values(data.errors).join(', ') : 'API request failed');
        const error = new Error(errMsg);
        error.status = response.status;
        error.data = data;
        throw error;
    }

    return data;
}
