"""
Configuration settings for the Chat Agent Flask application.
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration class."""
    
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = False
    TESTING = False
    
    # OpenAI settings
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # Database settings
    DATABASE_URL = os.getenv('DATABASE_URL')
    
    # File upload settings
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', str(16 * 1024 * 1024)))  # 16MB max file size
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx', 'xlsx', 'xls'}
    
    # Migration settings
    AUTO_MIGRATE = os.getenv('AUTO_MIGRATE', 'true').lower() == 'true'
    MIGRATIONS_DIR = os.getenv('MIGRATIONS_DIR', 'migrations')
    
    # RAG settings
    EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'text-embedding-3-small')
    CHAT_MODEL = os.getenv('CHAT_MODEL', 'gpt-4o')
    MAX_CONTEXT_LENGTH = int(os.getenv('MAX_CONTEXT_LENGTH', '1000'))
    DEFAULT_TOP_K = int(os.getenv('DEFAULT_TOP_K', '3'))
    
    # Text chunking settings
    MAX_TOKENS_PER_CHUNK = int(os.getenv('MAX_TOKENS_PER_CHUNK', '512'))  # Max tokens per chunk for embeddings
    CHUNK_OVERLAP_TOKENS = int(os.getenv('CHUNK_OVERLAP_TOKENS', '50'))   # Overlap tokens between chunks
    
    # Logging settings
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = os.getenv('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/app.log')
    LOG_BACKUP_COUNT = int(os.getenv('LOG_BACKUP_COUNT', '30'))  # Keep 30 days of logs
    ENABLE_FILE_LOGGING = os.getenv('ENABLE_FILE_LOGGING', 'true').lower() == 'true'
    ENABLE_REQUEST_LOGGING = os.getenv('ENABLE_REQUEST_LOGGING', 'true').lower() == 'true'
    
    @staticmethod
    def init_app(app):
        """Initialize application configuration."""
        # Ensure upload folder exists
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        
        # Ensure logs directory exists if file logging is enabled
        if app.config.get('ENABLE_FILE_LOGGING', True):
            log_dir = os.path.dirname(app.config.get('LOG_FILE', 'app.log'))
            if log_dir:
                os.makedirs(log_dir, exist_ok=True)


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'  # More verbose logging in development


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    LOG_LEVEL = 'INFO'   # Standard logging in production


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DATABASE_URL = os.getenv('TEST_DATABASE_URL', 'sqlite:///test.db')


# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
