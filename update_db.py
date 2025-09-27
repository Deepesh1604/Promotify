#!/usr/bin/env python3
"""
Database update script to recreate tables with proper cascade constraints
"""

from main import app
from models import db
import os
import shutil
from datetime import datetime

def backup_database():
    """Create a backup of the current database"""
    if os.path.exists('instance/app.db'):
        backup_name = f"instance/app_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        shutil.copy2('instance/app.db', backup_name)
        print(f"Database backed up to: {backup_name}")
        return backup_name
    return None

def update_database():
    """Update database with new cascade constraints"""
    with app.app_context():
        print("Updating database with cascade constraints...")
        
        # Drop all tables
        db.drop_all()
        print("Dropped all tables")
        
        # Recreate all tables with new constraints
        db.create_all()
        print("Created all tables with new constraints")
        
        print("Database update completed successfully!")

if __name__ == "__main__":
    print("Starting database update...")
    
    # Backup current database
    backup_file = backup_database()
    if backup_file:
        print(f"Current database backed up to: {backup_file}")
    
    try:
        # Update database
        update_database()
        print("\n✅ Database update completed successfully!")
        print("The campaign deletion functionality should now work properly.")
        
    except Exception as e:
        print(f"\n❌ Error updating database: {e}")
        if backup_file:
            print(f"You can restore from backup: {backup_file}")
        raise
