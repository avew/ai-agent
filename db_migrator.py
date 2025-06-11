import os
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseMigrator:
    """
    Handle database migrations automatically
    """
    
    def __init__(self, database_url, migrations_dir="migrations"):
        self.database_url = database_url
        self.migrations_dir = migrations_dir
        self.engine = create_engine(database_url, poolclass=NullPool)
    
    def check_table_exists(self, table_name):
        """Check if a table exists in the database"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = :table_name
                    );
                """), {"table_name": table_name}).fetchone()
                return result[0] if result else False
        except Exception as e:
            logger.error(f"Error checking table existence: {e}")
            return False
    
    def check_extension_exists(self, extension_name):
        """Check if PostgreSQL extension exists"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT EXISTS (
                        SELECT FROM pg_extension 
                        WHERE extname = :ext_name
                    );
                """), {"ext_name": extension_name}).fetchone()
                return result[0] if result else False
        except Exception as e:
            logger.error(f"Error checking extension: {e}")
            return False
    
    def run_migration_file(self, filename):
        """Run a specific migration file"""
        migration_path = os.path.join(self.migrations_dir, filename)
        
        if not os.path.exists(migration_path):
            logger.error(f"Migration file not found: {migration_path}")
            return False
        
        try:
            with open(migration_path, 'r', encoding='utf-8') as f:
                sql_content = f.read()
            
            with self.engine.begin() as conn:
                # Split SQL content by semicolon and execute each statement
                statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
                for statement in statements:
                    if statement:
                        conn.execute(text(statement))
            
            logger.info(f"Migration {filename} executed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error running migration {filename}: {e}")
            return False
    
    def auto_migrate(self):
        """
        Automatically run necessary migrations
        """
        logger.info("Checking database schema...")
        
        # Check if documents table exists
        if not self.check_table_exists('documents'):
            logger.info("Documents table not found. Running initial migration...")
            
            if self.run_migration_file('001_initial_schema.sql'):
                logger.info("✅ Initial migration completed successfully!")
                return True
            else:
                logger.error("❌ Initial migration failed!")
                return False
        else:
            logger.info("✅ Database schema is up to date")
            
            # Optional: Check if pgvector extension is enabled
            if not self.check_extension_exists('vector'):
                logger.warning("⚠️  pgvector extension is not enabled")
            
            return True
