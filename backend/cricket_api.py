import os
from datetime import timedelta

# Get base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)

# Database path
if os.environ.get('VERCEL') or os.environ.get('FLASK_ENV') == 'production':
    DATABASE_PATH = '/tmp/cricket.db'
    LOG_FILE = '/tmp/app.log'
    BACKUP_PATH = '/tmp/backups'
else:
    DATABASE_PATH = os.path.join(PROJECT_ROOT, 'database', 'cricket.db')
    LOG_FILE = os.path.join(PROJECT_ROOT, 'logs', 'app.log')
    BACKUP_PATH = os.path.join(PROJECT_ROOT, 'backups')

if not (os.environ.get('VERCEL') or os.environ.get('FLASK_ENV') == 'production'):
    try:
        os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        os.makedirs(BACKUP_PATH, exist_ok=True)
    except Exception as e:
        print(f"Warning: Could not create directories: {e}")

UPLOAD_FOLDER = os.path.join(PROJECT_ROOT, 'uploads')
PLAYER_UPLOAD_FOLDER = os.path.join(UPLOAD_FOLDER, 'players')
BACKGROUND_UPLOAD_FOLDER = os.path.join(UPLOAD_FOLDER, 'backgrounds')
SPONSOR_UPLOAD_FOLDER = os.path.join(UPLOAD_FOLDER, 'sponsors')
GENERATED_POSTS_FOLDER = os.path.join(UPLOAD_FOLDER, 'generated', 'manual_posts')
AUTO_POSTS_FOLDER = os.path.join(UPLOAD_FOLDER, 'generated', 'auto_posts')
WICKET_POSTS_FOLDER = os.path.join(UPLOAD_FOLDER, 'generated', 'wicket_posts')

for folder in [PLAYER_UPLOAD_FOLDER, BACKGROUND_UPLOAD_FOLDER, SPONSOR_UPLOAD_FOLDER, 
               GENERATED_POSTS_FOLDER, AUTO_POSTS_FOLDER, WICKET_POSTS_FOLDER]:
    try:
        os.makedirs(folder, exist_ok=True)
    except Exception as e:
        print(f"Warning: Could not create folder {folder}: {e}")

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
    TESTING = False
    HOST = '0.0.0.0'
    PORT = int(os.environ.get('PORT', 5000))
    
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=30)
    JWT_ALGORITHM = 'HS256'
    
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DATABASE_PATH}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'ttf'}
    
    CRICAPI_KEY = os.environ.get('CRICAPI_KEY', '')
    CRICAPI_BASE_URL = 'https://api.cricapi.com/v1'
    
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
    GEMINI_MODEL = 'gemini-pro'
    
    FACEBOOK_TOKEN = os.environ.get('FACEBOOK_TOKEN', '')
    FACEBOOK_PAGE_ID = os.environ.get('FACEBOOK_PAGE_ID', '')
    FACEBOOK_API_VERSION = 'v18.0'
    
    DATABASE_PATH = DATABASE_PATH
    LOG_FILE = LOG_FILE
    BACKUP_PATH = BACKUP_PATH
    UPLOAD_FOLDER = UPLOAD_FOLDER
    PLAYER_UPLOAD_FOLDER = PLAYER_UPLOAD_FOLDER
    BACKGROUND_UPLOAD_FOLDER = BACKGROUND_UPLOAD_FOLDER
    SPONSOR_UPLOAD_FOLDER = SPONSOR_UPLOAD_FOLDER
    GENERATED_POSTS_FOLDER = GENERATED_POSTS_FOLDER
    AUTO_POSTS_FOLDER = AUTO_POSTS_FOLDER
    WICKET_POSTS_FOLDER = WICKET_POSTS_FOLDER
    
    IMAGE_WIDTH = 1080
    IMAGE_HEIGHT = 1350
    IMAGE_QUALITY = 85
    PLAYER_IMAGE_SIZE = (400, 400)
    SPONSOR_SIZE = (200, 50)
    
    SCHEDULER_API_ENABLED = True
    SCHEDULER_TIMEZONE = 'UTC'
    SCORE_UPDATE_INTERVAL = 240
    
    FACEBOOK_QUEUE_ENABLED = True
    FACEBOOK_QUEUE_GAP_MINUTES = 1
    
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    
    FLASK_ENV = os.environ.get('FLASK_ENV', 'development')
    IS_PRODUCTION = FLASK_ENV == 'production' or bool(os.environ.get('VERCEL'))

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

config_name = os.environ.get('FLASK_ENV', 'development')
if config_name == 'production':
    config = ProductionConfig()
elif config_name == 'testing':
    config = TestingConfig()
else:
    config = DevelopmentConfig()
