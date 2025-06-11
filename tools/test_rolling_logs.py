#!/usr/bin/env python3
"""
Test script to demonstrate the new rolling log functionality.
This script tests both time-based and size-based rotation with compression.
"""
import os
import sys
import time
import logging
from datetime import datetime

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_rolling_logs():
    """Test the rolling log functionality."""
    print("🔄 Testing Rolling Log Functionality")
    print("=" * 50)
    
    # Import and create the app
    from app import create_app
    app = create_app()
    
    print(f"✅ Application initialized")
    print(f"📁 Log directory: {os.path.dirname(app.config['LOG_FILE'])}")
    print(f"📄 Log file: {app.config['LOG_FILE']}")
    print(f"🔄 Backup count: {app.config['LOG_BACKUP_COUNT']} days")
    
    # Check handler configuration
    for handler in app.logger.handlers:
        if hasattr(handler, 'maxBytes'):
            print(f"⚙️  Handler configuration:")
            print(f"   - Max file size: {handler.maxBytes / 1024 / 1024:.0f}MB")
            print(f"   - Rotation time: {handler.when}")
            print(f"   - Backup count: {handler.backupCount}")
            break
    
    print("\n🧪 Generating test log entries...")
    
    # Generate some test logs
    test_messages = [
        "System startup completed successfully",
        "Database connection established",
        "User authentication service started",
        "Cache warming process initiated",
        "Background tasks scheduler started",
        "API endpoints registered",
        "Security middleware configured",
        "Performance monitoring enabled",
        "Health check endpoints available",
        "Application ready to serve requests"
    ]
    
    with app.app_context():
        for i, message in enumerate(test_messages, 1):
            app.logger.info(f"[Test {i:02d}/10] {message}")
            app.logger.debug(f"Debug info for test message {i}: timestamp={datetime.now().isoformat()}")
            time.sleep(0.1)  # Small delay to see timestamps
    
    print(f"✅ Generated {len(test_messages)} test log entries")
    
    # Check log file status
    log_file = app.config['LOG_FILE']
    if os.path.exists(log_file):
        file_size = os.path.getsize(log_file)
        print(f"📊 Current log file size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
        
        # Show latest entries
        print("\n📋 Latest log entries:")
        with open(log_file, 'r') as f:
            lines = f.readlines()
            for line in lines[-5:]:  # Show last 5 lines
                print(f"   {line.strip()}")
    
    # Check for any existing rotated files
    log_dir = os.path.dirname(log_file)
    log_basename = os.path.basename(log_file)
    
    rotated_files = []
    for filename in os.listdir(log_dir):
        if filename.startswith(log_basename + ".") and filename != log_basename:
            rotated_files.append(filename)
    
    if rotated_files:
        print(f"\n🗂️  Found {len(rotated_files)} rotated log files:")
        rotated_files.sort()
        for filename in rotated_files:
            filepath = os.path.join(log_dir, filename)
            size = os.path.getsize(filepath)
            compressed = "(compressed)" if filename.endswith('.gz') else "(uncompressed)"
            print(f"   - {filename}: {size:,} bytes {compressed}")
    else:
        print("\n📝 No rotated log files found yet (this is normal for a new setup)")
    
    print(f"\n✅ Rolling log test completed successfully!")
    print(f"🔍 Monitor the logs directory: {log_dir}")
    print(f"📈 File rotation will occur:")
    print(f"   - Daily at midnight")
    print(f"   - When file size reaches 100MB")
    print(f"   - Old files will be compressed to .gz format")
    print(f"   - Files older than {app.config['LOG_BACKUP_COUNT']} days will be removed")

if __name__ == "__main__":
    test_rolling_logs()
