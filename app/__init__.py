"""
Application factory for the Chat Agent Flask app.
"""
import os
import logging
import logging.handlers
import gzip
import shutil
import time
from datetime import datetime
from flask import Flask
from .config import config


class CustomTimedRotatingFileHandler(logging.handlers.TimedRotatingFileHandler):
    """
    Custom TimedRotatingFileHandler that also rotates based on file size
    and compresses old log files with gzip.
    """
    
    def __init__(self, filename, when='h', interval=1, maxBytes=0, backupCount=0, 
                 encoding=None, delay=False, utc=False, atTime=None):
        super().__init__(filename, when, interval, backupCount, encoding, delay, utc, atTime)
        self.maxBytes = maxBytes
        
    def shouldRollover(self, record):
        """
        Determine if rollover should occur.
        
        Returns True if either:
        1. Time-based rotation is due (parent class logic)
        2. File size exceeds maxBytes
        """
        # Check time-based rotation first
        if super().shouldRollover(record):
            return True
            
        # Check size-based rotation
        if self.maxBytes > 0:
            msg = "%s\n" % self.format(record)
            self.stream.seek(0, 2)  # Due to non-posix-compliant Windows feature
            if self.stream.tell() + len(msg) >= self.maxBytes:
                return True
                
        return False
    
    def doRollover(self):
        """
        Do a rollover; in this case, a date/time stamp is appended to the filename
        when the rollover happens. However, you want the file to be named for the
        start of the interval, not the current time. If there is a backup count,
        then we have to get a list of matching filenames, sort them and remove
        the one with the oldest suffix.
        """
        if self.stream:
            self.stream.close()
            self.stream = None
            
        # Get the time that this sequence started at and make it a TimeTuple
        currentTime = int(time.time())
        dstNow = time.localtime(currentTime)[-1]
        t = self.rolloverAt - self.interval
        if self.utc:
            timeTuple = time.gmtime(t)
        else:
            timeTuple = time.localtime(t)
            dstThen = timeTuple[-1]
            if dstNow != dstThen:
                if dstNow:
                    addend = 3600
                else:
                    addend = -3600
                timeTuple = time.localtime(t + addend)
                
        dfn = self.rotation_filename(self.baseFilename + "." + 
                                   time.strftime(self.suffix, timeTuple))
        
        if os.path.exists(dfn):
            os.remove(dfn)
            
        self.rotate(self.baseFilename, dfn)
        
        # Compress the rotated file
        self._compress_file(dfn)
        
        if self.backupCount > 0:
            for s in self.getFilesToDelete():
                os.remove(s)
                
        if not self.delay:
            self.stream = self._open()
            
        newRolloverAt = self.computeRollover(currentTime)
        while newRolloverAt <= currentTime:
            newRolloverAt = newRolloverAt + self.interval
        self.rolloverAt = newRolloverAt
    
    def _compress_file(self, source_file):
        """Compress the source file to gzip format and remove the original."""
        try:
            with open(source_file, 'rb') as f_in:
                with gzip.open(f"{source_file}.gz", 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            # Remove the original uncompressed file
            os.remove(source_file)
        except Exception as e:
            # If compression fails, keep the original file
            logging.getLogger(__name__).warning(f"Failed to compress log file {source_file}: {e}")
    
    def getFilesToDelete(self):
        """
        Determine the files to delete when rolling over.
        More specific than the earlier method, which just used glob.glob().
        """
        dirName, baseName = os.path.split(self.baseFilename)
        fileNames = os.listdir(dirName)
        result = []
        prefix = baseName + "."
        plen = len(prefix)
        for fileName in fileNames:
            if fileName[:plen] == prefix:
                suffix = fileName[plen:]
                # Look for both compressed (.gz) and uncompressed files
                if suffix.endswith('.gz'):
                    suffix = suffix[:-3]  # Remove .gz extension
                if self.extMatch.match(suffix):
                    result.append(os.path.join(dirName, fileName))
        if len(result) < self.backupCount:
            result = []
        else:
            result.sort()
            result = result[:len(result) - self.backupCount]
        return result


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
    """Configure application logging with daily rotation and size limits."""
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
            
            # Create custom handler with daily rotation and size limits
            file_handler = CustomTimedRotatingFileHandler(
                app.config['LOG_FILE'],
                when='midnight',           # Rotate daily at midnight
                interval=1,                # Every 1 day
                maxBytes=104857600,        # 100MB max file size
                backupCount=app.config.get('LOG_BACKUP_COUNT', 30),  # Keep 30 days of logs
                encoding='utf-8',
                delay=False,
                utc=False,
                atTime=None
            )
            file_handler.setLevel(log_level)
            file_handler.setFormatter(formatter)
            app.logger.addHandler(file_handler)
        except Exception as e:
            app.logger.warning(f"Could not set up file logging: {e}")
    
    # Prevent duplicate logs
    app.logger.propagate = False
    
    # Log configuration
    log_file_info = f"Log File: {app.config['LOG_FILE']}" if app.config['ENABLE_FILE_LOGGING'] else ""
    app.logger.info(f"Logging configured - Level: {app.config['LOG_LEVEL']} | "
                   f"File Logging: {app.config['ENABLE_FILE_LOGGING']} | {log_file_info}")


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
