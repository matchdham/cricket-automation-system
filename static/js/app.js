// ============================================
// FILE: app.js
// PURPOSE: Main dashboard JavaScript logic
// Tab functions, API calls, DOM manipulation
// ============================================

// ============================================
// GLOBAL VARIABLES
// ============================================

let currentTab = 1;
let token = localStorage.getItem('token');
let userId = localStorage.getItem('user_id');
let userRole = localStorage.getItem('role');
let username = localStorage.getItem('username');

// ============================================
// INITIALIZATION
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    console.log('Dashboard loaded');
    
    // User display करो
    document.getElementById('userDisplay').textContent = `${username} (${userRole})`;
    
    // Initial data load करो
    loadCounters();
    loadPosts();
    loadHealthStatus();
    loadPlayers();
});

// ============================================
// TAB SWITCHING
// ============================================

function switchTab(tabNumber) {
    // सभी tabs hide करो
    const tabs = document.querySelectorAll('.tab-content');
    tabs.forEach(tab => tab.classList.remove('active'));
    
    // सभी buttons inactive करो
    const buttons = document.querySelectorAll('.tab-button');
    buttons.forEach(btn => btn.classList.remove('active'));
    
    // Selected tab show करो
    document.getElementById(`tab${tabNumber}`).classList.add('active');
    buttons[tabNumber - 1].classList.add('active');
    
    currentTab = tabNumber;
    console.log(`Switched to tab ${tabNumber}`);
}

// ============================================
// TAB 1: CREATE POST
// ============================================

async function createPost() {
    try {
        const newsTitle = document.getElementById('newsTitle').value.trim();
        const aiPrompt = document.getElementById('aiPrompt').value.trim();
        const useCustomBg = document.getElementById('bgToggle').classList.contains('active');
        
        if (!newsTitle) {
            showMessage('postMessage', 'Please enter news title', 'error');
            return;
        }
        
        // Show loading
        const btn = event.target;
        btn.disabled = true;
        btn.textContent = 'Creating...';
        
        const response = await fetch('/api/create-post', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                news_title: newsTitle,
                ai_prompt: aiPrompt,
                use_custom_bg: useCustomBg
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showMessage('postMessage', '✓ Post created and queued for Facebook!', 'success');
            
            // Clear form
            document.getElementById('newsTitle').value = '';
            document.getElementById('aiPrompt').value = '';
            
            // Show preview
            if (data.image_url) {
                const preview = `
                    <div style="margin-top: 15px; background: white; padding: 12px; border-radius: 8px;">
                        <img src="${data.image_url}" style="width: 100%; border-radius: 6px; margin-bottom: 10px;">
                        <div style="font-size: 12px; color: #666;">
                            <strong>Caption:</strong> ${data.caption}<br>
                            <strong>Hashtags:</strong> ${data.hashtags}
                        </div>
                    </div>
                `;
                document.getElementById('postMessage').innerHTML += preview;
            }
            
            // Reload counters
            loadCounters();
        } else {
            showMessage('postMessage', data.message || 'Failed to create post', 'error');
        }
    } catch (error) {
        showMessage('postMessage', 'Error: ' + error.message, 'error');
        console.error('Create post error:', error);
    } finally {
        event.target.disabled = false;
        event.target.textContent = 'Generate & Post';
    }
}

function toggleBg() {
    const toggle = document.getElementById('bgToggle');
    toggle.classList.toggle('active');
}

// ============================================
// TAB 2: DESIGN SETTINGS
// ============================================

async function uploadBackground() {
    try {
        const file = document.getElementById('bgFile').files[0];
        
        if (!file) {
            alert('Please select a background image');
            return;
        }
        
        const formData = new FormData();
        formData.append('background', file);
        
        const response = await fetch('/api/upload-background', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert('✓ Background uploaded!');
            document.getElementById('bgFile').value = '';
        } else {
            alert('Error: ' + data.message);
        }
    } catch (error) {
        alert('Upload error: ' + error.message);
        console.error('Upload error:', error);
    }
}

async function uploadSponsor() {
    try {
        const file = document.getElementById('sponsorFile').files[0];
        
        if (!file) {
            alert('Please select a sponsor logo');
            return;
        }
        
        const formData = new FormData();
        formData.append('sponsor', file);
        
        const response = await fetch('/api/upload-sponsor', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert('✓ Sponsor logo uploaded!');
            document.getElementById('sponsorFile').value = '';
        } else {
            alert('Error: ' + data.message);
        }
    } catch (error) {
        alert('Upload error: ' + error.message);
    }
}

function toggleLogoBold() {
    const toggle = document.getElementById('logoBoldToggle');
    toggle.classList.toggle('active');
}

function toggleTextBold() {
    const toggle = document.getElementById('textBoldToggle');
    toggle.classList.toggle('active');
}

function toggleTodayMode() {
    const toggle = document.getElementById('todayModeToggle');
    toggle.classList.toggle('active');
}

async function saveSettings() {
    try {
        const logoBold = document.getElementById('logoBoldToggle').classList.contains('active');
        const textBold = document.getElementById('textBoldToggle').classList.contains('active');
        const todayMode = document.getElementById('todayModeToggle').classList.contains('active');
        
        const response = await fetch('/api/toggle-settings', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                logo_bold: logoBold,
                text_bold: textBold,
                today_match_mode: todayMode
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert('✓ Settings saved!');
        } else {
            alert('Error: ' + data.message);
        }
    } catch (error) {
        alert('Error: ' + error.message);
        console.error('Save settings error:', error);
    }
}

// ============================================
// TAB 3: PLAYER VAULT
// ============================================

async function uploadPlayer() {
    try {
        const name = document.getElementById('playerName').value.trim();
        const file = document.getElementById('playerImage').files[0];
        
        if (!name || !file) {
            alert('Please enter player name and select image');
            return;
        }
        
        const formData = new FormData();
        formData.append('player_name', name);
        formData.append('player_image', file);
        
        const response = await fetch('/api/upload-player', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert('✓ Player added!');
            document.getElementById('playerName').value = '';
            document.getElementById('playerImage').value = '';
            loadPlayers();
        } else {
            alert('Error: ' + data.message);
        }
    } catch (error) {
        alert('Error: ' + error.message);
        console.error('Upload player error:', error);
    }
}

async function loadPlayers() {
    try {
        const response = await fetch('/api/get-players', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        const data = await response.json();
        
        if (data.success && data.players) {
            let html = '<div class="player-grid">';
            
            data.players.forEach(player => {
                html += `
                    <div class="player-card">
                        <img src="${player.image_path}" alt="${player.name}" class="player-image">
                        <div class="player-name">${player.name}</div>
                        <button class="delete-btn" onclick="deletePlayer(${player.id})">Delete</button>
                    </div>
                `;
            });
            
            html += '</div>';
            document.getElementById('playersList').innerHTML = html;
        }
    } catch (error) {
        console.error('Load players error:', error);
    }
}

async function deletePlayer(playerId) {
    if (!confirm('Delete this player?')) return;
    
    try {
        const response = await fetch(`/api/delete-player/${playerId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            loadPlayers();
        } else {
            alert('Error: ' + data.message);
        }
    } catch (error) {
        alert('Error: ' + error.message);
        console.error('Delete player error:', error);
    }
}

// ============================================
// TAB 4: LIVE LEDGER
// ============================================

async function loadCounters() {
    try {
        const response = await fetch('/api/get-counters', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            document.getElementById('todayCreated').textContent = data.today_created;
            document.getElementById('todayPosted').textContent = data.today_posted;
            document.getElementById('totalCreated').textContent = data.total_created;
            document.getElementById('totalPosted').textContent = data.total_posted;
        }
    } catch (error) {
        console.error('Load counters error:', error);
    }
}

async function loadPosts() {
    try {
        const response = await fetch('/api/get-posts', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        const data = await response.json();
        
        if (data.success && data.posts) {
            let html = '';
            
            data.posts.forEach(post => {
                const badge = post.posted ? 
                    '<span class="badge posted">✓ Posted</span>' : 
                    '<span class="badge pending">⏳ Pending</span>';
                
                html += `
                    <div class="post-item">
                        <div>
                            <div class="post-title">${post.title}</div>
                            <div class="post-status">${post.created}</div>
                        </div>
                        <div>${badge}</div>
                    </div>
                `;
            });
            
            document.getElementById('postsList').innerHTML = html;
        }
    } catch (error) {
        console.error('Load posts error:', error);
    }
}

async function loadHealthStatus() {
    try {
        const response = await fetch('/api/health-status', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            const statusClass = data.status === 'online' ? 'online' : 'offline';
            const statusText = data.status === 'online' ? '🟢 Online' : '🔴 Offline';
            
            let html = `
                <div class="health-status ${statusClass}">
                    <span class="status-dot"></span>
                    ${statusText}
                </div>
            `;
            
            if (data.recent_logs && data.recent_logs.length > 0) {
                html += '<h5 style="margin-top: 10px; margin-bottom: 8px; font-size: 12px;">Recent Activity:</h5>';
                
                data.recent_logs.forEach(log => {
                    html += `<div style="font-size: 11px; color: #666; margin-bottom: 4px;">
                        ${log.message}
                    </div>`;
                });
            }
            
            document.getElementById('healthStatus').innerHTML = html;
        }
    } catch (error) {
        console.error('Load health status error:', error);
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
    if (confirm('Are you sure you want to logout?')) {
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

// हर 30 seconds में counters refresh करो
setInterval(() => {
    if (currentTab === 4) {
        loadCounters();
        loadPosts();
        loadHealthStatus();
    }
}, 30000);

console.log('✅ Dashboard app.js loaded');