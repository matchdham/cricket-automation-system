# ============================================
# FILE: config.py
# PURPOSE: App Global Configuration & Environment Settings (Option B - Static Paths)
# ============================================

import os
from datetime import timedelta

# Get base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)

# Database path - Railway/Vercel (Production check)
if os.environ.get('VERCEL') or os.environ.get('FLASK_ENV') == 'production' or os.environ.get('RAILWAY_ENVIRONMENT'):
    DATABASE_PATH = '/tmp/cricket.db'
    LOG_FILE = '/tmp/app.log'
    BACKUP_PATH = '/tmp/backups'
else:
    # Local development
    DATABASE_PATH = os.path.join(PROJECT_ROOT, 'database', 'cricket.db')
    LOG_FILE = os.path.join(PROJECT_ROOT, 'logs', 'app.log')
    BACKUP_PATH = os.path.join(PROJECT_ROOT, 'backups')

# Create directories only in development (not in server production)
if not (os.environ.get('VERCEL') or os.environ.get('FLASK_ENV') == 'production' or os.environ.get('RAILWAY_ENVIRONMENT')):
    try:
        os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        os.makedirs(BACKUP_PATH, exist_ok=True)
    except Exception as e:
        print(f"Warning: Could not create directories: {e}")

# ============================================
# OPTION B: UPLOAD PATHS FIXED TO STATIC
# ============================================
STATIC_FOLDER = os.path.join(PROJECT_ROOT, 'static')
UPLOAD_FOLDER = os.path.join(STATIC_FOLDER, 'uploads')

# Ab saari images directly static/uploads ke andar jayengi taaki browser directly padh sake
PLAYER_UPLOAD_FOLDER = os.path.join(UPLOAD_FOLDER, 'players')
BACKGROUND_UPLOAD_FOLDER = os.path.join(UPLOAD_FOLDER, 'backgrounds')
SPONSOR_UPLOAD_FOLDER = os.path.join(UPLOAD_FOLDER, 'sponsors')
GENERATED_POSTS_FOLDER = os.path.join(UPLOAD_FOLDER, 'generated', 'manual_posts')
AUTO_POSTS_FOLDER = os.path.join(UPLOAD_FOLDER, 'generated', 'auto_posts')
WICKET_POSTS_FOLDER = os.path.join(UPLOAD_FOLDER, 'generated', 'wicket_posts')

# Shorthand paths jo tumhaari baki files backend me use karti hain
PLAYERS_FOLDER = PLAYER_UPLOAD_FOLDER
BACKGROUNDS_FOLDER = BACKGROUND_UPLOAD_FOLDER
SPONSORS_FOLDER = SPONSOR_UPLOAD_FOLDER
PLAYER_IMAGE_SIZE = (400, 400)
WORKER_CAN_EDIT_CAPTION = True

# Create upload directories automatically
for folder in [PLAYER_UPLOAD_FOLDER, BACKGROUND_UPLOAD_FOLDER, SPONSOR_UPLOAD_FOLDER, 
               GENERATED_POSTS_FOLDER, AUTO_POSTS_FOLDER, WICKET_POSTS_FOLDER]:
    try:
        os.makedirs(folder, exist_ok=True)
    except Exception as e:
        print(f"Warning: Could not create folder {folder}: {e}")

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production-32-chars-min')
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
    TESTING = False
    BCRYPT_LOG_ROUNDS = 12

    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # JWT SETTINGS
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production-32-chars')
    JWT_ALGORITHM = 'HS256'
    JWT_EXPIRATION_HOURS = 24
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=30)
    
    # Database
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DATABASE_PATH}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    
    # Shorthand properties
    PLAYERS_FOLDER = PLAYERS_FOLDER
    BACKGROUNDS_FOLDER = BACKGROUNDS_FOLDER
    SPONSORS_FOLDER = SPONSORS_FOLDER
    PLAYER_IMAGE_SIZE = PLAYER_IMAGE_SIZE
    WORKER_CAN_EDIT_CAPTION = WORKER_CAN_EDIT_CAPTION
    
    # API keys
    CRICAPI_KEY = os.environ.get('CRICAPI_KEY', '')
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
    FACEBOOK_TOKEN = os.environ.get('FACEBOOK_TOKEN', '')
    FACEBOOK_PAGE_ID = os.environ.get('FACEBOOK_PAGE_ID', '')
    
    # Paths
    DATABASE_PATH = DATABASE_PATH
    LOG_FILE = LOG_FILE
    BACKUP_PATH = BACKUP_PATH
    UPLOAD_FOLDER = UPLOAD_FOLDER
    
    # Scheduler
    SCHEDULER_API_ENABLED = True
    SCHEDULER_TIMEZONE = "UTC"
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    
    # Environment
    FLASK_ENV = os.environ.get('FLASK_ENV', 'development')
    IS_PRODUCTION = FLASK_ENV == 'production' or bool(os.environ.get('VERCEL')) or bool(os.environ.get('RAILWAY_ENVIRONMENT'))

class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

# Select config based on environment
config_name = os.environ.get('FLASK_ENV', 'development')
if config_name == 'production' or os.environ.get('RAILWAY_ENVIRONMENT'):
    config = ProductionConfig()
elif config_name == 'testing':
    config = TestingConfig()
else:
    config = DevelopmentConfig()
    
