# ============================================
# FILE: config.py
# PURPOSE: सभी configuration एक जगह
# ============================================

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    
    # Flask Settings
    FLASK_ENV = os.getenv("FLASK_ENV", "production")
    DEBUG = os.getenv("DEBUG", "False") == "True"
    SECRET_KEY = os.getenv("SECRET_KEY", "cricket-dashboard-secret-2024")
    HOST = "0.0.0.0"
    PORT = int(os.getenv("PORT", 5000))
    
    # Database
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DATABASE_PATH = os.path.join(BASE_DIR, '..', 'database', 'cricket.db')
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    
    # API Keys
    CRICAPI_KEY = os.getenv("CRICAPI_KEY", "26d7de00-35e1-47a8-aea7-54b76903ba57")
    CRICAPI_BASE_URL = "https://api.cricapi.com/v1"
    
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL = "gemini-pro"
    
    FACEBOOK_TOKEN = os.getenv("FACEBOOK_TOKEN", "your_facebook_token_here")
    FACEBOOK_PAGE_ID = os.getenv("FACEBOOK_PAGE_ID", "")
    FACEBOOK_API_VERSION = "v18.0"
    
    # Upload Folders
    UPLOAD_BASE_FOLDER = os.path.join(BASE_DIR, '..', 'uploads')
    PLAYERS_FOLDER = os.path.join(UPLOAD_BASE_FOLDER, 'players')
    BACKGROUNDS_FOLDER = os.path.join(UPLOAD_BASE_FOLDER, 'backgrounds')
    SPONSORS_FOLDER = os.path.join(UPLOAD_BASE_FOLDER, 'sponsors')
    GENERATED_FOLDER = os.path.join(UPLOAD_BASE_FOLDER, 'generated')
    AUTO_POSTS_FOLDER = os.path.join(GENERATED_FOLDER, 'auto_posts')
    MANUAL_POSTS_FOLDER = os.path.join(GENERATED_FOLDER, 'manual_posts')
    WICKET_POSTS_FOLDER = os.path.join(GENERATED_FOLDER, 'wicket_posts')
    
    FONTS_FOLDER = os.path.join(BASE_DIR, '..', 'static', 'fonts')
    
    # File Settings
    MAX_FILE_SIZE = 10 * 1024 * 1024
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'ttf'}
    
    for folder in [PLAYERS_FOLDER, BACKGROUNDS_FOLDER, SPONSORS_FOLDER,
                   AUTO_POSTS_FOLDER, MANUAL_POSTS_FOLDER, WICKET_POSTS_FOLDER]:
        os.makedirs(folder, exist_ok=True)
    
    # Image Settings
    IMAGE_WIDTH = 1080
    IMAGE_HEIGHT = 1350
    IMAGE_QUALITY = 85
    IMAGE_COMPRESS_ENABLED = True
    
    PLAYER_IMAGE_SIZE = (400, 400)
    SPONSOR_SIZE = (200, 50)
    SPONSOR_POSITION = "bottom-right"
    SPONSOR_MARGIN = 20
    
    # Caption Settings
    MAX_CAPTION_LENGTH = 50
    CAPTION_INCLUDE_EVENT = True
    CAPTION_INCLUDE_PLAYER = True
    CAPTION_INCLUDE_OVER = True
    
    # Hashtag Settings
    HASHTAG_INCLUDE_MATCH = True
    HASHTAG_INCLUDE_PLAYER = True
    HASHTAG_INCLUDE_TRENDING = True
    HASHTAG_LANGUAGE = "mixed"
    
    # Scheduler (4-min)
    SCORE_UPDATE_INTERVAL = 4 * 60
    AUTO_TRACK_DEFAULT = True
    PARALLEL_TRACKING_ENABLED = True
    
    # Facebook Queue
    FACEBOOK_QUEUE_ENABLED = True
    FACEBOOK_QUEUE_GAP_MINUTES = 1
    AUTO_POST_TO_FACEBOOK = True
    
    # Rate Limiting
    GEMINI_RATE_LIMIT = 60
    GEMINI_RATE_LIMIT_ENABLED = True
    TEMPLATE_FALLBACK_ENABLED = True
    
    # Database Backup
    DATABASE_BACKUP_ENABLED = True
    DATABASE_BACKUP_FREQUENCY = "daily"
    BACKUP_FOLDER = os.path.join(BASE_DIR, '..', 'backups')
    os.makedirs(BACKUP_FOLDER, exist_ok=True)
    
    # Worker Permissions
    WORKER_CAN_CREATE_POST = True
    WORKER_CAN_UPLOAD_PLAYER = True
    WORKER_CAN_VIEW_HEALTH = True
    WORKER_CAN_EDIT_SETTINGS = False
    WORKER_CAN_EDIT_CAPTION = True
    WORKER_CAN_EDIT_HASHTAGS = True
    
    # Boss Permissions
    BOSS_FULL_CONTROL = True
    BOSS_CAN_OVERRIDE_SETTINGS = True
    BOSS_CAN_MANAGE_ADMINS = True
    BOSS_CAN_MANAGE_WORKERS = True
    BOSS_REAL_TIME_DASHBOARD = True
    
    # Default User
    DEFAULT_ADMIN_USERNAME = "admin"
    DEFAULT_ADMIN_PASSWORD = "admin123"
    
    # Logging
    LOG_LEVEL = "INFO"
    LOG_FILE = os.path.join(BASE_DIR, '..', 'logs', 'app.log')
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    
    # Security
    BCRYPT_LOG_ROUNDS = 12
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-secret-key-change-in-production")
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRATION_HOURS = 24
    
    # Cricket Data
    MATCH_TYPES = ["T20", "ODI", "Test"]
    EVENT_TYPES = {
        "wicket": "Wicket",
        "milestone": "Milestone",
        "century": "Century",
        "fifty": "50 runs",
        "match_complete": "Match Complete"
    }
    MILESTONES = [6, 10, 15, 20]
    
    # Mobile First
    MOBILE_FIRST = True
    LANDSCAPE_MODE_ENABLED = False
    LAZY_LOADING_ENABLED = True
    IMAGE_OPTIMIZATION_ENABLED = True
    
    # Render Cloud
    RENDER_ENVIRONMENT = os.getenv("RENDER", False)
    if RENDER_ENVIRONMENT:
        DATABASE_PATH = "/var/data/cricket.db"
    
    # Theme
    PRIMARY_COLOR = "#1e5ba8"
    SECONDARY_COLOR = "#ff6b35"
    SUCCESS_COLOR = "#2ecc71"
    ERROR_COLOR = "#e74c3c"
    
    DEFAULT_LANGUAGE = "hinglish"

config = Config()

def check_required_env_vars():
    """Check सभी zaroori environment variables"""
    required_vars = ["CRICAPI_KEY", "GEMINI_API_KEY"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️ Missing: {missing_vars}")
        return False, missing_vars
    
    print("✅ All environment variables set!")
    return True, []