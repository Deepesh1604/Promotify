#!/usr/bin/env python3
"""
Complete database rebuild with wallet functionality
"""

from main import app
from models import db
import os
import shutil
from datetime import datetime

def rebuild_database():
    """Completely rebuild database with wallet tables"""
    with app.app_context():
        print("🔄 Starting complete database rebuild...")
        
        # Backup existing database if it exists
        if os.path.exists('instance/app.db'):
            backup_name = f"instance/app_backup_wallet_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            shutil.copy2('instance/app.db', backup_name)
            print(f"📁 Database backed up to: {backup_name}")
        
        # Remove existing database
        if os.path.exists('instance/app.db'):
            os.remove('instance/app.db')
            print("🗑️ Removed existing database")
        
        # Create all tables fresh with wallet functionality
        db.create_all()
        print("✅ Created all tables with wallet functionality")
        
        print("\n🎉 Database rebuild completed successfully!")
        print("   - All tables recreated with wallet support")
        print("   - Ready for fresh data setup")

if __name__ == "__main__":
    rebuild_database()
