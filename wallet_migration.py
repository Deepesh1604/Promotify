#!/usr/bin/env python3
"""
Database migration script to add wallet functionality
"""

from main import app
from models import db
import sqlite3
from datetime import datetime

def migrate_database():
    """Add wallet fields to existing database"""
    with app.app_context():
        db_path = 'instance/app.db'
        
        try:
            # Connect to database
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            print("Adding wallet fields to database...")
            
            # Add wallet_balance to sponsor table
            try:
                cursor.execute("ALTER TABLE sponsor ADD COLUMN wallet_balance REAL DEFAULT 0.0")
                print("✅ Added wallet_balance to sponsor table")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e):
                    print("⚠️ wallet_balance already exists in sponsor table")
                else:
                    raise
            
            # Add wallet fields to influencer table
            try:
                cursor.execute("ALTER TABLE influencer ADD COLUMN wallet_balance REAL DEFAULT 0.0")
                print("✅ Added wallet_balance to influencer table")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e):
                    print("⚠️ wallet_balance already exists in influencer table")
                else:
                    raise
                    
            try:
                cursor.execute("ALTER TABLE influencer ADD COLUMN bank_account VARCHAR(20)")
                print("✅ Added bank_account to influencer table")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e):
                    print("⚠️ bank_account already exists in influencer table")
                else:
                    raise
                    
            try:
                cursor.execute("ALTER TABLE influencer ADD COLUMN ifsc_code VARCHAR(11)")
                print("✅ Added ifsc_code to influencer table")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e):
                    print("⚠️ ifsc_code already exists in influencer table")
                else:
                    raise
            
            conn.commit()
            conn.close()
            
            print("\n🎉 Database migration completed successfully!")
            
            # Create new tables using SQLAlchemy
            print("Creating new wallet tables...")
            db.create_all()
            print("✅ Wallet tables created successfully!")
            
        except Exception as e:
            print(f"❌ Migration error: {e}")
            raise

if __name__ == "__main__":
    print("🔄 Starting wallet database migration...")
    migrate_database()
    print("\n✅ Migration completed! Wallet functionality is now available.")
