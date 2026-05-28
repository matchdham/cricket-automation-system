// ============================================
// FILE: user_management.js
// PURPOSE: User management utilities
// Permission checking, role management
// ============================================

// ============================================
// PERMISSION CHECKING
// ============================================

class PermissionManager {
    constructor() {
        this.role = localStorage.getItem('role');
        this.permissions = {
            'boss': {
                'create_admin': true,
                'delete_admin': true,
                'manage_workers': true,
                'override_settings': true,
                'view_audit_logs': true,
                'reset_password': true,
                'create_post': true,
                'edit_post': true,
                'delete_post': true,
                'upload_player': true,
                'delete_player': true,
                'upload_background': true,
                'upload_sponsor': true,
                'toggle_settings': true,
                'view_dashboard': true,
                'view_health': true,
                'auto_track': true
            },
            'admin': {
                'create_admin': false,
                'delete_admin': false,
                'manage_workers': true,
                'override_settings': false,
                'view_audit_logs': false,
                'reset_password': false,
                'create_post': true,
                'edit_post': true,
                'delete_post': false,
                'upload_player': true,
                'delete_player': true,
                'upload_background': true,
                'upload_sponsor': true,
                'toggle_settings': true,
                'view_dashboard': true,
                'view_health': true,
                'auto_track': false
            },
            'worker': {
                'create_admin': false,
                'delete_admin': false,
                'manage_workers': false,
                'override_settings': false,
                'view_audit_logs': false,
                'reset_password': false,
                'create_post': true,
                'edit_post': true,
                'delete_post': false,
                'upload_player': true,
                'delete_player': false,
                'upload_background': false,
                'upload_sponsor': false,
                'toggle_settings': false,
                'view_dashboard': true,
                'view_health': true,
                'auto_track': false
            }
        };
    }
    
    // Check करो कि user के पास permission है
    hasPermission(permission) {
        if (!this.role || !this.permissions[this.role]) {
            return false;
        }
        
        return this.permissions[this.role][permission] === true;
    }
    
    // Multiple permissions check करो (सभी होने चाहिए)
    hasAllPermissions(permissionList) {
        return permissionList.every(perm => this.hasPermission(perm));
    }
    
    // कम से कम एक permission है?
    hasAnyPermission(permissionList) {
        return permissionList.some(perm => this.hasPermission(perm));
    }
    
    // Role level get करो
    getRoleLevel() {
        const levels = {
            'boss': 3,
            'admin': 2,
            'worker': 1
        };
        return levels[this.role] || 0;
    }
    
    // उच्च role है?
    isHigherRole(otherRole) {
        const levels = {
            'boss': 3,
            'admin': 2,
            'worker': 1
        };
        return (levels[this.role] || 0) > (levels[otherRole] || 0);
    }
}

// Global permission manager
const permissionManager = new PermissionManager();

// ============================================
// UI PERMISSION CONTROL
// ============================================

function enableFeatureIf(permission, elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        if (!permissionManager.hasPermission(permission)) {
            element.style.display = 'none';
        }
    }
}

function disableButtonIf(permission, buttonId) {
    const button = document.getElementById(buttonId);
    if (button) {
        if (!permissionManager.hasPermission(permission)) {
            button.disabled = true;
            button.style.opacity = '0.5';
            button.title = 'You do not have permission to use this feature';
        }
    }
}

// ============================================
// USER SESSION MANAGEMENT
// ============================================

class UserSession {
    constructor() {
        this.token = localStorage.getItem('token');
        this.userId = localStorage.getItem('user_id');
        this.role = localStorage.getItem('role');
        this.username = localStorage.getItem('username');
    }
    
    isLoggedIn() {
        return !!this.token && !!this.userId;
    }
    
    hasRole(role) {
        return this.role === role;
    }
    
    isBoss() {
        return this.role === 'boss';
    }
    
    isAdmin() {
        return this.role === 'admin';
    }
    
    isWorker() {
        return this.role === 'worker';
    }
    
    logout() {
        localStorage.removeItem('token');
        localStorage.removeItem('user_id');
        localStorage.removeItem('role');
        localStorage.removeItem('username');
        window.location.href = '/';
    }
    
    getHeaders() {
        return {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${this.token}`
        };
    }
}

// Global user session
const userSession = new UserSession();

// ============================================
// ROUTE PROTECTION
// ============================================

function protectRoute(requiredRole) {
    if (!userSession.isLoggedIn()) {
        window.location.href = '/';
        return false;
    }
    
    if (requiredRole && userSession.role !== requiredRole && userSession.role !== 'boss') {
        alert('Access denied. You do not have permission to view this page.');
        window.location.href = '/dashboard';
        return false;
    }
    
    return true;
}

// ============================================
// API CALL UTILITIES
// ============================================

async function apiCall(endpoint, method = 'GET', data = null) {
    try {
        const options = {
            method: method,
            headers: userSession.getHeaders()
        };
        
        if (data) {
            options.body = JSON.stringify(data);
        }
        
        const response = await fetch(endpoint, options);
        
        if (response.status === 401) {
            // Token expired
            userSession.logout();
            return null;
        }
        
        return await response.json();
    } catch (error) {
        console.error('API call error:', error);
        return null;
    }
}

// ============================================
// TOKEN REFRESH
// ============================================

function setupTokenRefresh() {
    // हर 12 hours में token refresh करने की check करो
    setInterval(() => {
        if (!userSession.isLoggedIn()) {
            userSession.logout();
        }
    }, 12 * 60 * 60 * 1000);
}

// On page load, check token
window.addEventListener('load', () => {
    if (!userSession.isLoggedIn()) {
        window.location.href = '/';
    }
    setupTokenRefresh();
});

// ============================================
// LOGGING
// ============================================

class Logger {
    static log(message) {
        console.log(`[${new Date().toLocaleTimeString()}] ${message}`);
    }
    
    static error(message, error = null) {
        console.error(`[ERROR] ${message}`, error);
    }
    
    static warn(message) {
        console.warn(`[WARNING] ${message}`);
    }
}

// ============================================
// EXPORTS
// ============================================

// ये functions globally available हैं

// Permission check करने के लिए:
// permissionManager.hasPermission('create_post')

// User session check करने के लिए:
// userSession.isLoggedIn()
// userSession.isBoss()

// API call के लिए:
// apiCall('/api/endpoint', 'POST', {data})

// Route protect करने के लिए:
// protectRoute('admin')

// Logging के लिए:
// Logger.log('message')
// Logger.error('message', error)

console.log('✅ User management.js loaded');