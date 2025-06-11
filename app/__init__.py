"""
Application factory for the Chat Agent Flask app.
"""
import os
from flask import Flask
from .config import config


def create_app(config_name=None):
    """Create and configure the Flask application."""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'default')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
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
