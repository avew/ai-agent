"""
Application factory for the Chat Agent Flask app.
"""
import os
import logging
import logging.handlers
from flask import Flask
from .config import config


def create_app(config_name=None):
    """Create and configure the Flask application."""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'default')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Configure logging
    configure_logging(app)
    
    # Configure request logging middleware
    configure_request_logging(app)
    
    # Initialize database migration if enabled
    if app.config['AUTO_MIGRATE']:
        with app.app_context():
            try:
                print("🔄 Running auto-migration check...")
                from .database.migrator import DatabaseMigrator
                migrator = DatabaseMigrator(
                    app.config['DATABASE_URL'],
                    app.config['MIGRATIONS_DIR']
                )
                migrator.auto_migrate()
            except Exception as e:
                print(f"❌ Database migration check failed: {e}")
                print("⚠️  Application will continue, but database functionality may not work properly.")
                print("Please run migration manually: python -m app.database.migrator")
    else:
        print("⏭️  Auto-migration disabled. Set AUTO_MIGRATE=true to enable.")
    
    # Register blueprints
    from .routes import register_blueprints
    register_blueprints(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    return app


def register_error_handlers(app):
    """Register error handlers."""
    
    @app.errorhandler(404)
    def not_found(error):
        return {"error": "Resource not found"}, 404
    
    @app.errorhandler(400)
    def bad_request(error):
        return {"error": "Bad request"}, 400
    
    @app.errorhandler(500)
    def internal_error(error):
        return {"error": "Internal server error"}, 500
    
    @app.errorhandler(413)
    def file_too_large(error):
        return {"error": "File too large"}, 413


def configure_logging(app):
    """Configure application logging."""
    # Set log level
    log_level = getattr(logging, app.config['LOG_LEVEL'].upper(), logging.INFO)
    app.logger.setLevel(log_level)
    
    # Remove default handlers
    for handler in app.logger.handlers[:]:
        app.logger.removeHandler(handler)
    
    # Create formatter
    formatter = logging.Formatter(app.config['LOG_FORMAT'])
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    app.logger.addHandler(console_handler)
    
    # File handler (if enabled)
    if app.config['ENABLE_FILE_LOGGING']:
        try:
            # Ensure logs directory exists
            log_dir = os.path.dirname(app.config['LOG_FILE'])
            if log_dir:
                os.makedirs(log_dir, exist_ok=True)
            
            file_handler = logging.handlers.RotatingFileHandler(
                app.config['LOG_FILE'],
                maxBytes=10485760,  # 10MB
                backupCount=5
            )
            file_handler.setLevel(log_level)
            file_handler.setFormatter(formatter)
            app.logger.addHandler(file_handler)
        except Exception as e:
            app.logger.warning(f"Could not set up file logging: {e}")
    
    # Prevent duplicate logs
    app.logger.propagate = False
    
    # Log configuration
    app.logger.info(f"Logging configured - Level: {app.config['LOG_LEVEL']} | "
                   f"File Logging: {app.config['ENABLE_FILE_LOGGING']}")


def configure_request_logging(app):
    """Configure HTTP request logging middleware."""
    
    # Only enable request logging if configured
    if not app.config.get('ENABLE_REQUEST_LOGGING', True):
        return
    
    @app.before_request
    def log_request_info():
        """Log incoming HTTP requests."""
        from flask import request
        app.logger.info(f"HTTP Request: {request.method} {request.path} | "
                       f"Remote Addr: {request.remote_addr} | "
                       f"User Agent: {request.headers.get('User-Agent', 'Unknown')}")
    
    @app.after_request  
    def log_response_info(response):
        """Log HTTP response."""
        from flask import request
        app.logger.info(f"HTTP Response: {request.method} {request.path} | "
                       f"Status: {response.status_code} | "
                       f"Content Length: {response.content_length or 0}")
        return response
