"""
Database migration script to add CampaignInvitation table
Run this script to add the new invitation functionality to existing databases
"""

from flask import Flask
from models import db, CampaignInvitation
import os

def migrate_database():
    """Add CampaignInvitation table to existing database"""
    
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize the database with the app
    db.init_app(app)
    
    with app.app_context():
        try:
            # Create the new table
            db.create_all()
            print("✅ Successfully added CampaignInvitation table to the database!")
            
            # Check if table was created
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            if 'campaign_invitation' in tables:
                print("✅ CampaignInvitation table created successfully!")
                
                # Show table structure
                columns = inspector.get_columns('campaign_invitation')
                print("\n📋 CampaignInvitation table structure:")
                for column in columns:
                    print(f"   - {column['name']}: {column['type']}")
            else:
                print("❌ CampaignInvitation table was not created")
                
        except Exception as e:
            print(f"❌ Error during migration: {e}")
            return False
    
    return True

if __name__ == "__main__":
    print("🚀 Starting database migration...")
    print("📝 Adding CampaignInvitation table for invitation functionality")
    
    success = migrate_database()
    
    if success:
        print("\n✅ Migration completed successfully!")
        print("🎉 Your database is now ready for the invitation functionality!")
    else:
        print("\n❌ Migration failed!")
        print("Please check the error messages above and try again.")
