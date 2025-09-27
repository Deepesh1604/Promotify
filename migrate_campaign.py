#!/usr/bin/env python3
"""
Database migration script to add created_at field to Campaign table
"""
import sqlite3
from datetime import datetime
import os

def migrate_database():
    db_path = 'instance/app.db'
    
    if not os.path.exists(db_path):
        print("Database not found. Creating new database...")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if created_at column already exists
        cursor.execute("PRAGMA table_info(campaign)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'created_at' not in columns:
            print("Adding created_at column to campaign table...")
            
            # Add the created_at column with a default value
            cursor.execute("ALTER TABLE campaign ADD COLUMN created_at DATETIME")
            
            # Update existing campaigns with a default created_at timestamp
            default_timestamp = datetime.utcnow().isoformat()
            cursor.execute("UPDATE campaign SET created_at = ? WHERE created_at IS NULL", (default_timestamp,))
            
            conn.commit()
            print("Successfully added created_at column to campaign table")
        else:
            print("created_at column already exists in campaign table")
            
    except Exception as e:
        print(f"Error during migration: {e}")
        conn.rollback()
    
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()
