// Authentication utilities
function getToken() {
    return localStorage.getItem('token');
}

function setToken(token) {
    localStorage.setItem('token', token);
}

function removeToken() {
    localStorage.removeItem('token');
}

function isAuthenticated() {
    return !!getToken();
}

// API utilities
async function fetchWithAuth(url, options = {}) {
    const token = getToken();
    const headers = {
        'Content-Type': 'application/json',
        ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
        ...options.headers
    };

    const response = await fetch(url, {
        ...options,
        headers
    });

    if (response.status === 401) {
        // Token expired or invalid
        removeToken();
        window.location.href = '/login';
        return;
    }

    return response;
}

// Application utilities
function formatDate(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

function formatCurrency(amount) {
    if (!amount) return '';
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        maximumFractionDigits: 0
    }).format(amount);
}

// Status utilities
function getStatusClass(status) {
    const statusClasses = {
        'applied': 'status-applied',
        'interview': 'status-interview',
        'offer': 'status-offer',
        'rejected': 'status-rejected',
        'withdrawn': 'status-withdrawn'
    };
    return statusClasses[status.toLowerCase()] || 'status-default';
}

// Initialize Alpine.js data
document.addEventListener('alpine:init', () => {
    Alpine.store('auth', {
        token: getToken(),
        isAuthenticated: isAuthenticated,
        logout() {
            removeToken();
            window.location.href = '/login';
        }
    });
});

// Export utilities
window.jobTrackUtils = {
    fetchWithAuth,
    formatDate,
    formatCurrency,
    getStatusClass,
    getToken,
    setToken,
    removeToken,
    isAuthenticated
};
