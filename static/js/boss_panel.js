// ============================================
// FILE: boss_panel.js
// PURPOSE: Boss panel JavaScript logic
// Admin/Worker management, audit logs
// ============================================

// ============================================
// GLOBAL VARIABLES
// ============================================

let token = localStorage.getItem('token');
let userId = localStorage.getItem('user_id');
let currentTab = 'admins';

// ============================================
// INITIALIZATION
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    console.log('Boss panel loaded');
    
    // Initial data load करो
    loadDashboardOverview();
    loadUsers();
    loadAuditLogs();
});

// ============================================
// TAB SWITCHING
// ============================================

function switchTab(tabName) {
    // सभी tabs hide करो
    const tabs = document.querySelectorAll('.tab-content');
    tabs.forEach(tab => tab.classList.remove('active'));
    
    // सभी buttons inactive करो
    const buttons = document.querySelectorAll('.tab-btn');
    buttons.forEach(btn => btn.classList.remove('active'));
    
    // Selected tab show करो
    document.getElementById(tabName).classList.add('active');
    event.target.classList.add('active');
    
    currentTab = tabName;
}

// ============================================
// DASHBOARD OVERVIEW
// ============================================

async function loadDashboardOverview() {
    try {
        const response = await fetch('/api/boss/dashboard-overview', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            document.getElementById('adminCount').textContent = data.admin_count;
            document.getElementById('workerCount').textContent = data.worker_count;
            document.getElementById('totalPosts').textContent = data.total_posts;
            document.getElementById('totalPosted').textContent = data.total_posted;
        }
    } catch (error) {
        console.error('Load overview error:', error);
    }
}

// ============================================
// CREATE ADMIN
// ============================================

async function createAdmin() {
    try {
        const username = document.getElementById('newAdminUsername').value.trim();
        const password = document.getElementById('newAdminPassword').value;
        
        if (!username || !password) {
            showMessage('createMessage', 'Please enter username and password', 'error');
            return;
        }
        
        const response = await fetch('/api/boss/create-admin', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                username: username,
                password: password
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showMessage('createMessage', `✓ Admin '${username}' created!`, 'success');
            document.getElementById('newAdminUsername').value = '';
            document.getElementById('newAdminPassword').value = '';
            
            // Reload users और overview
            loadUsers();
            loadDashboardOverview();
        } else {
            showMessage('createMessage', 'Error: ' + data.message, 'error');
        }
    } catch (error) {
        showMessage('createMessage', 'Error: ' + error.message, 'error');
        console.error('Create admin error:', error);
    }
}

// ============================================
// USER MANAGEMENT
// ============================================

async function loadUsers() {
    try {
        const response = await fetch('/api/boss/get-users', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        const data = await response.json();
        
        if (data.success && data.users) {
            let adminsHtml = '';
            let workersHtml = '';
            
            data.users.forEach(hierarchy => {
                const admin = hierarchy.admin;
                
                adminsHtml += `
                    <div class="user-item">
                        <div class="user-info">
                            <div class="user-name">${admin.username}</div>
                            <div class="user-role">Admin • ${admin.created_at}</div>
                        </div>
                        <div class="user-actions">
                            <button class="action-btn" onclick="resetPassword(${admin.id})">Reset</button>
                            <button class="action-btn" onclick="deleteAdmin(${admin.id})">Delete</button>
                        </div>
                    </div>
                `;
                
                // Workers
                if (hierarchy.workers && hierarchy.workers.length > 0) {
                    hierarchy.workers.forEach(worker => {
                        workersHtml += `
                            <div class="user-item" style="border-left-color: #ff6b35;">
                                <div class="user-info">
                                    <div class="user-name">${worker.username}</div>
                                    <div class="user-role">Worker under ${admin.username} • ${worker.created_at}</div>
                                </div>
                                <div class="user-actions">
                                    <button class="action-btn" onclick="resetPassword(${worker.id})">Reset</button>
                                </div>
                            </div>
                        `;
                    });
                }
            });
            
            document.getElementById('adminsList').innerHTML = adminsHtml || '<p>No admins</p>';
            document.getElementById('workersList').innerHTML = workersHtml || '<p>No workers</p>';
        }
    } catch (error) {
        console.error('Load users error:', error);
    }
}

async function deleteAdmin(adminId) {
    if (!confirm('Delete this admin? All workers will be transferred to another admin.')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/boss/delete-admin`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                admin_id: adminId
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert('✓ Admin deleted. Workers transferred.');
            loadUsers();
            loadDashboardOverview();
        } else {
            alert('Error: ' + data.message);
        }
    } catch (error) {
        alert('Error: ' + error.message);
        console.error('Delete admin error:', error);
    }
}

async function resetPassword(userId) {
    const newPassword = prompt('Enter new password:');
    if (!newPassword) return;
    
    try {
        const response = await fetch('/api/boss/reset-password', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                user_id: userId,
                new_password: newPassword
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert('✓ Password reset!');
            loadAuditLogs();
        } else {
            alert('Error: ' + data.message);
        }
    } catch (error) {
        alert('Error: ' + error.message);
        console.error('Reset password error:', error);
    }
}

// ============================================
// AUDIT LOGS
// ============================================

async function loadAuditLogs() {
    try {
        const response = await fetch('/api/boss/audit-logs', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        const data = await response.json();
        
        if (data.success && data.logs) {
            let html = '';
            
            data.logs.forEach(log => {
                html += `
                    <div class="log-item">
                        <div class="log-action">
                            ${log.action.toUpperCase()}
                        </div>
                        <div>${log.details}</div>
                        <div class="log-time">${log.timestamp}</div>
                    </div>
                `;
            });
            
            document.getElementById('auditLogsList').innerHTML = html || '<p>No logs</p>';
        }
    } catch (error) {
        console.error('Load audit logs error:', error);
    }
}

// ============================================
// HELPER FUNCTIONS
// ============================================

function showMessage(elementId, message, type) {
    const element = document.getElementById(elementId);
    element.innerHTML = `<div class="message ${type}">${message}</div>`;
}

function logout() {
    if (confirm('Logout?')) {
        localStorage.removeItem('token');
        localStorage.removeItem('user_id');
        localStorage.removeItem('role');
        localStorage.removeItem('username');
        window.location.href = '/';
    }
}

// ============================================
// AUTO REFRESH
// ============================================

// हर 1 minute में data refresh करो
setInterval(() => {
    loadDashboardOverview();
    loadUsers();
    loadAuditLogs();
}, 60000);

console.log('✅ Boss panel app.js loaded');