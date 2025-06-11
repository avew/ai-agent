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
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx', 'xlsx', 'xls'}
    
    # Migration settings
    AUTO_MIGRATE = os.getenv('AUTO_MIGRATE', 'true').lower() == 'true'
    MIGRATIONS_DIR = 'migrations'
    
    # RAG settings
    EMBEDDING_MODEL = "text-embedding-3-small"
    CHAT_MODEL = "gpt-4o"
    MAX_CONTEXT_LENGTH = 1000
    DEFAULT_TOP_K = 3
    
    @staticmethod
    def init_app(app):
        """Initialize application configuration."""
        # Ensure upload folder exists
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False


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
