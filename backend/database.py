# ============================================
# FILE: database.py
# PURPOSE: SQLite database operations
# ============================================

import sqlite3
import os
from datetime import datetime
from .config import config

DATABASE_PATH = 'database.db'
def init_database():
    """
    Database को initialize करो
    सभी tables create करो
    Default admin user बनाओ
    """
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Users Table (Admin, Worker, Boss)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT DEFAULT 'worker',
                created_by INTEGER,
                status TEXT DEFAULT 'active',
                parent_admin_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(created_by) REFERENCES users(id),
                FOREIGN KEY(parent_admin_id) REFERENCES users(id)
            )
        ''')
        
        # Players Table (Khiladi Database)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                cricapi_player_id TEXT,
                image_path TEXT NOT NULL,
                position TEXT,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Posts Table (Generated Graphics)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                news_title TEXT NOT NULL,
                image_path TEXT NOT NULL,
                ai_prompt TEXT,
                caption TEXT,
                hashtags TEXT,
                background_type TEXT,
                posted_to_facebook BOOLEAN DEFAULT 0,
                facebook_post_id TEXT,
                created_by INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                posted_at TIMESTAMP,
                FOREIGN KEY(created_by) REFERENCES users(id)
            )
        ''')
        
        # Settings Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                admin_id INTEGER,
                use_fixed_background BOOLEAN DEFAULT 0,
                fixed_background_path TEXT,
                is_today_match_mode BOOLEAN DEFAULT 0,
                logo_bold BOOLEAN DEFAULT 0,
                text_bold BOOLEAN DEFAULT 1,
                sponsor_logo_path TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(admin_id) REFERENCES users(id)
            )
        ''')
        
        # System Logs Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                log_type TEXT,
                message TEXT,
                error_details TEXT,
                affected_post_id INTEGER,
                affected_user_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(affected_post_id) REFERENCES posts(id),
                FOREIGN KEY(affected_user_id) REFERENCES users(id)
            )
        ''')
        
        # Lifecycle Counter
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS lifecycle_counter (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                total_images_created INTEGER DEFAULT 0,
                total_images_posted INTEGER DEFAULT 0,
                today_created INTEGER DEFAULT 0,
                today_posted INTEGER DEFAULT 0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Audit Logs (Boss Activity)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                boss_id INTEGER,
                action TEXT,
                affected_user_id INTEGER,
                details TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(boss_id) REFERENCES users(id),
                FOREIGN KEY(affected_user_id) REFERENCES users(id)
            )
        ''')
        
        # Facebook Queue
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS facebook_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER,
                queued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                posted_at TIMESTAMP,
                status TEXT DEFAULT 'pending',
                FOREIGN KEY(post_id) REFERENCES posts(id)
            )
        ''')
        
        conn.commit()
        
    #Check if default admin exists        
       cursor.execute('SELECT COUNT(*) FROM users WHERE role="admin")
       if cursor.fetchone()[0] 0:
           from .auth import hash password
            admin hash = hash password(config.DEFAULT_ADMIN_PASSWORD)
            cursor.execute("""
              INSERT INTO users (username, password_hash, role)
              VALUES (?, ?, 7)
            """,(config.DEFAULT ADMIN USERNAME, admin hash, 'admin'))
            conn.commit()
            print(" Default admin created! (admin/admin123)")
        
        # Initialize lifecycle counter
        cursor.execute('SELECT COUNT(*) FROM lifecycle_counter')
        if cursor.fetchone()[0] == 0:
            cursor.execute('''
                INSERT INTO lifecycle_counter 
                (total_images_created, total_images_posted, today_created, today_posted)
                VALUES (0, 0, 0, 0)
            ''')
            conn.commit()
        
        conn.close()
        print("✅ Database initialized!")
        return True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def get_db_connection():
    """Database connection लो"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def execute_query(query, params=None):
    """Single query execute करो"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Query error: {e}")
        return False

def fetch_one(query, params=None):
    """एक row fetch करो"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        result = cursor.fetchone()
        conn.close()
        return result
    except Exception as e:
        print(f"❌ Fetch error: {e}")
        return None

def fetch_all(query, params=None):
    """सभी rows fetch करो"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        results = cursor.fetchall()
        conn.close()
        return results
    except Exception as e:
        print(f"❌ Fetch all error: {e}")
        return []

def log_error(log_type, message, error_details=None, post_id=None, user_id=None):
    """System log में error save करो"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO system_logs 
            (log_type, message, error_details, affected_post_id, affected_user_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (log_type, message, error_details, post_id, user_id))
        
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"❌ Log error: {e}")

def backup_database():
    """Daily manual backup"""
    try:
        import shutil
        from datetime import datetime
        
        backup_name = f"cricket_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        backup_path = os.path.join(config.BACKUP_FOLDER, backup_name)
        
        shutil.copy2(DATABASE_PATH, backup_path)
        print(f"✅ Backup created: {backup_path}")
        return True
    except Exception as e:
        print(f"❌ Backup error: {e}")
        return False
