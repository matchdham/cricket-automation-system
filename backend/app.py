# ============================================
# FILE: app.py
# PURPOSE: Main Flask Server - सभी routes
# ============================================

from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import os
import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import json

# Import करो सभी modules
from .config import config
from .auth import hash_password, verify_password, generate_jwt_token, verify_jwt_token
from .database import init_database, get_db_connection, log_error, fetch_one, fetch_all, execute_query
from .cricket_api import get_current_matches, get_match_info
from .image_generator import create_graphic_with_text
from .caption_generator import generate_caption_with_hashtags
from .facebook_poster import schedule_facebook_post

# Flask app initialize करो
app = Flask(__name__, 
            template_folder='../templates',
            static_folder='../static')
CORS(app)
# Configurat
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = 'uploads'
# Database initialize करो
init_database()

# ============================================
# HELPER FUNCTIONS
# ============================================

def require_login(f):
    """Decorator - Login required"""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'success': False, 'message': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'success': False, 'message': 'Token missing'}), 401
        
        payload = verify_jwt_token(token)
        if not payload:
            return jsonify({'success': False, 'message': 'Invalid or expired token'}), 401
        
        request.user_id = payload['user_id']
        request.username = payload['username']
        request.role = payload['role']
        
        return f(*args, **kwargs)
    
    return decorated_function

def require_role(required_role):
    """Decorator - Role check"""
    from functools import wraps
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = None
            if 'Authorization' in request.headers:
                auth_header = request.headers['Authorization']
                try:
                    token = auth_header.split(" ")[1]
                except IndexError:
                    return jsonify({'success': False, 'message': 'Invalid token format'}), 401
            
            if not token:
                return jsonify({'success': False, 'message': 'Token missing'}), 401
            
            payload = verify_jwt_token(token)
            if not payload:
                return jsonify({'success': False, 'message': 'Invalid or expired token'}), 401
            
            if payload['role'] not in [required_role, 'boss']:
                return jsonify({'success': False, 'message': f'Only {required_role} can access'}), 403
            
            request.user_id = payload['user_id']
            request.username = payload['username']
            request.role = payload['role']
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    return decorator

# ============================================
# AUTHENTICATION ROUTES
# ============================================

@app.route('/api/login', methods=['POST'])
def api_login():
    """
    User login करो
    REQUEST: {"username": "admin", "password": "admin123"}
    RESPONSE: {"success": true, "token": "...", "user_id": 1, "role": "admin"}
    """
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'success': False, 'message': 'Username/password required'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()
        
        if not user:
            log_error('login_failed', f'User not found: {username}')
            return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
        
        if not verify_password(password, user['password_hash']):
            log_error('login_failed', f'Wrong password: {username}')
            return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
        
        token = generate_jwt_token(user['id'], user['username'], user['role'])
        
        log_error('success', f'Login successful: {username}')
        
        return jsonify({
            'success': True,
            'token': token,
            'user_id': user['id'],
            'role': user['role'],
            'username': user['username']
        })
    
    except Exception as e:
        log_error('api_error', 'Login failed', str(e))
        return jsonify({'success': False, 'message': str(e)}), 500

# ============================================
# TAB 1: LIVE NEWS & POST COMMAND
# ============================================

@app.route('/api/create-post', methods=['POST'])
@require_login
def api_create_post():
    """
    Tab 1: Manual news input → Auto-caption + Graphic create
    """
    try:
        data = request.json
        news_title = data.get('news_title', '')
        ai_prompt = data.get('ai_prompt', '')
        use_custom_bg = data.get('use_custom_bg', False)
        
        if not news_title:
            return jsonify({'success': False, 'message': 'News title required'}), 400
        
        # Settings लो
        settings = fetch_one('SELECT * FROM settings WHERE id = 1')
        sponsor_logo = settings['sponsor_logo_path'] if settings else None
        text_bold = settings['text_bold'] if settings else False
        
        # Background image
        background_image = None
        if use_custom_bg and settings and settings['fixed_background_path']:
            background_image = settings['fixed_background_path']
        
        # Gemini से auto-caption generate करो
        caption_data = generate_caption_with_hashtags(news_title, ai_prompt)
        caption = caption_data.get('caption', news_title)
        hashtags = caption_data.get('hashtags', '#cricket #live')
        
        final_caption = f"{caption}\n{hashtags}"
        
        # Image generate करो
        image_path = create_graphic_with_text(
            news_title=final_caption,
            background_image=background_image,
            text_bold=text_bold,
            sponsor_logo=sponsor_logo,
            ai_prompt=ai_prompt
        )
        
        if not image_path:
            return jsonify({'success': False, 'message': 'Failed to create graphic'}), 500
        
        # Database में save करो
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO posts 
            (news_title, image_path, ai_prompt, caption, hashtags, background_type, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (news_title, image_path, ai_prompt, caption, hashtags, 
              'custom' if use_custom_bg else 'default', request.user_id))
        
        post_id = cursor.lastrowid
        
        # Counter update करो
        cursor.execute('''
            UPDATE lifecycle_counter 
            SET total_images_created = total_images_created + 1,
                today_created = today_created + 1
            WHERE id = 1
        ''')
        
        # Facebook queue में add करो
        cursor.execute('''
            INSERT INTO facebook_queue (post_id, status)
            VALUES (?, 'pending')
        ''', (post_id,))
        
        conn.commit()
        conn.close()
        
        log_error('success', f'Post created: {post_id}')
        
        return jsonify({
            'success': True,
            'post_id': post_id,
            'image_url': f'/uploads/generated/{os.path.basename(image_path)}',
            'caption': caption,
            'hashtags': hashtags
        })
    
    except Exception as e:
        log_error('api_error', 'Failed to create post', str(e))
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/edit-caption', methods=['POST'])
@require_login
def api_edit_caption():
    """
    Tab 1: Worker caption को edit कर सकता है
    """
    try:
        data = request.json
        post_id = data.get('post_id')
        new_caption = data.get('caption')
        new_hashtags = data.get('hashtags')
        
        if not post_id or not new_caption:
            return jsonify({'success': False, 'message': 'Post ID and caption required'}), 400
        
        # Check permissions
        if request.role == 'worker' and not config.WORKER_CAN_EDIT_CAPTION:
            return jsonify({'success': False, 'message': 'Permission denied'}), 403
        
        # Update करो
        execute_query('''
            UPDATE posts 
            SET caption = ?, hashtags = ?
            WHERE id = ?
        ''', (new_caption, new_hashtags or '#cricket #live', post_id))
        
        log_error('success', f'Caption edited: {post_id}')
        
        return jsonify({'success': True, 'message': 'Caption updated'})
    
    except Exception as e:
        log_error('api_error', 'Caption edit failed', str(e))
        return jsonify({'success': False, 'message': str(e)}), 500

# ============================================
# TAB 2: DESIGN CONTROL
# ============================================

@app.route('/api/upload-background', methods=['POST'])
@require_login
@require_role('admin')
def api_upload_background():
    """Tab 2: Custom background upload"""
    try:
        if 'background' not in request.files:
            return jsonify({'success': False, 'message': 'No file provided'}), 400
        
        file = request.files['background']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No file selected'}), 400
        
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"bg_{timestamp}_{filename}"
        filepath = os.path.join(config.BACKGROUNDS_FOLDER, filename)
        
        file.save(filepath)
        
        # Settings update करो
        execute_query('''
            UPDATE settings 
            SET fixed_background_path = ?, use_fixed_background = 1
            WHERE id = 1
        ''', (filepath,))
        
        log_error('success', 'Background uploaded')
        
        return jsonify({
            'success': True,
            'message': 'Background uploaded',
            'file_path': filepath
        })
    
    except Exception as e:
        log_error('file_upload', 'Background upload failed', str(e))
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/upload-sponsor', methods=['POST'])
@require_login
@require_role('admin')
def api_upload_sponsor():
    """Tab 2: Sponsor logo upload"""
    try:
        if 'sponsor' not in request.files:
            return jsonify({'success': False, 'message': 'No file'}), 400
        
        file = request.files['sponsor']
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"sponsor_{timestamp}_{filename}"
        filepath = os.path.join(config.SPONSORS_FOLDER, filename)
        
        file.save(filepath)
        
        execute_query('''
            UPDATE settings 
            SET sponsor_logo_path = ?
            WHERE id = 1
        ''', (filepath,))
        
        log_error('success', 'Sponsor logo uploaded')
        
        return jsonify({'success': True, 'message': 'Sponsor uploaded'})
    
    except Exception as e:
        log_error('file_upload', 'Sponsor upload failed', str(e))
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/toggle-settings', methods=['POST'])
@require_login
@require_role('admin')
def api_toggle_settings():
    """Tab 2: Toggle bold, today's match mode"""
    try:
        data = request.json
        logo_bold = data.get('logo_bold', False)
        text_bold = data.get('text_bold', False)
        today_match_mode = data.get('today_match_mode', False)
        
        execute_query('''
            UPDATE settings 
            SET logo_bold = ?, text_bold = ?, is_today_match_mode = ?
            WHERE id = 1
        ''', (logo_bold, text_bold, today_match_mode))
        
        log_error('success', 'Settings updated')
        
        return jsonify({'success': True, 'message': 'Settings updated'})
    
    except Exception as e:
        log_error('api_error', 'Settings update failed', str(e))
        return jsonify({'success': False, 'message': str(e)}), 500

# ============================================
# TAB 3: PLAYER VAULT
# ============================================

@app.route('/api/upload-player', methods=['POST'])
@require_login
def api_upload_player():
    """Tab 3: Add player to vault"""
    try:
        player_name = request.form.get('player_name', '')
        
        if 'player_image' not in request.files or not player_name:
            return jsonify({'success': False, 'message': 'Name and image required'}), 400
        
        file = request.files['player_image']
        
        # Image resize करो (400x400)
        from PIL import Image
        img = Image.open(file)
        img = img.resize((config.PLAYER_IMAGE_SIZE[0], config.PLAYER_IMAGE_SIZE[1]))
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{secure_filename(player_name)}_{timestamp}.png"
        image_path = os.path.join(config.PLAYERS_FOLDER, filename)
        
        img.save(image_path, 'PNG')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO players (name, image_path)
                VALUES (?, ?)
            ''', (player_name, image_path))
            
            conn.commit()
            conn.close()
            
            log_error('success', f'Player added: {player_name}')
            
            return jsonify({
                'success': True,
                'message': f'{player_name} added',
                'image_path': image_path
            })
        
        except sqlite3.IntegrityError:
            conn.close()
            return jsonify({'success': False, 'message': 'Player already exists'}), 400
    
    except Exception as e:
        log_error('file_upload', 'Player upload failed', str(e))
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/get-players', methods=['GET'])
@require_login
def api_get_players():
    """Tab 3: Get all players"""
    try:
        players = fetch_all('SELECT id, name, image_path FROM players')
        
        players_list = [
            {'id': p['id'], 'name': p['name'], 'image_path': p['image_path']}
            for p in players
        ]
        
        return jsonify({'success': True, 'players': players_list})
    
    except Exception as e:
        log_error('api_error', 'Failed to get players', str(e))
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/delete-player/<int:player_id>', methods=['DELETE'])
@require_login
def api_delete_player(player_id):
    """Tab 3: Delete player"""
    try:
        player = fetch_one('SELECT image_path FROM players WHERE id = ?', (player_id,))
        
        if not player:
            return jsonify({'success': False, 'message': 'Player not found'}), 404
        
        if os.path.exists(player['image_path']):
            os.remove(player['image_path'])
        
        execute_query('DELETE FROM players WHERE id = ?', (player_id,))
        
        log_error('success', f'Player deleted: {player_id}')
        
        return jsonify({'success': True, 'message': 'Player deleted'})
    
    except Exception as e:
        log_error('api_error', 'Failed to delete player', str(e))
        return jsonify({'success': False, 'message': str(e)}), 500

# ============================================
# TAB 4: LIVE LEDGER
# ============================================

@app.route('/api/get-counters', methods=['GET'])
@require_login
def api_get_counters():
    """Tab 4: Get counters"""
    try:
        counter = fetch_one('SELECT * FROM lifecycle_counter WHERE id = 1')
        
        if counter:
            return jsonify({
                'success': True,
                'today_created': counter['today_created'],
                'today_posted': counter['today_posted'],
                'total_created': counter['total_images_created'],
                'total_posted': counter['total_images_posted']
            })
        
        return jsonify({
            'success': True,
            'today_created': 0,
            'today_posted': 0,
            'total_created': 0,
            'total_posted': 0
        })
    
    except Exception as e:
        log_error('api_error', 'Failed to get counters', str(e))
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/get-posts', methods=['GET'])
@require_login
def api_get_posts():
    """Tab 4: Get all posts"""
    try:
        posts = fetch_all('''
            SELECT id, news_title, created_at, posted_to_facebook 
            FROM posts 
            ORDER BY created_at DESC 
            LIMIT 100
        ''')
        
        posts_list = [
            {
                'id': p['id'],
                'title': p['news_title'],
                'created': p['created_at'],
                'posted': p['posted_to_facebook']
            }
            for p in posts
        ]
        
        return jsonify({'success': True, 'posts': posts_list})
    
    except Exception as e:
        log_error('api_error', 'Failed to get posts', str(e))
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/health-status', methods=['GET'])
@require_login
def api_health_status():
    """Tab 4: System health"""
    try:
        conn = get_db_connection()
        conn.execute('SELECT 1').fetchone()
        
        recent_logs = fetch_all('''
            SELECT log_type, message, created_at 
            FROM system_logs 
            ORDER BY created_at DESC 
            LIMIT 5
        ''')
        
        conn.close()
        
        recent_logs_list = [
            {
                'type': e['log_type'],
                'message': e['message'],
                'time': e['created_at']
            }
            for e in recent_logs
        ]
        
        status = 'online' if not any(e['type'] == 'error' for e in recent_logs_list) else 'error'
        
        return jsonify({
            'success': True,
            'status': status,
            'recent_logs': recent_logs_list
        })
    
    except Exception as e:
        log_error('api_error', 'Health check failed', str(e))
        return jsonify({'success': False, 'status': 'error'}), 500

# ============================================
# PAGES
# ============================================

@app.route('/')
def index():
    """Login page"""
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    """Main dashboard"""
    return render_template('dashboard.html')

@app.route('/boss-panel')
def boss_panel():
    """Boss control panel"""
    return render_template('boss_panel.html')

# ============================================
# ERROR HANDLERS
# ==========================================
