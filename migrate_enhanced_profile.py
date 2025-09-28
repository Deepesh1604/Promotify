#!/usr/bin/env python3
"""
Enhanced Profile Migration Script
Adds new fields to the Influencer model for social media metrics and profile details
"""

from main import app
from models import db, Influencer
from sqlalchemy import text

def upgrade_database():
    """Add new columns to the influencer table"""
    with app.app_context():
        # Check if the new columns already exist
        inspector = db.inspect(db.engine)
        columns = [column['name'] for column in inspector.get_columns('influencer')]
        
        new_columns = [
            ('bio', 'TEXT'),
            ('niche', 'VARCHAR(100)'),
            ('secondary_niches', 'VARCHAR(200)'),
            ('instagram_followers', 'INTEGER DEFAULT 0'),
            ('instagram_url', 'VARCHAR(200)'),
            ('youtube_subscribers', 'INTEGER DEFAULT 0'),
            ('youtube_url', 'VARCHAR(200)'),
            ('twitter_followers', 'INTEGER DEFAULT 0'),
            ('twitter_url', 'VARCHAR(200)'),
            ('linkedin_connections', 'INTEGER DEFAULT 0'),
            ('linkedin_url', 'VARCHAR(200)'),
            ('engagement_rate', 'FLOAT DEFAULT 0.0'),
            ('profile_verified', 'BOOLEAN DEFAULT FALSE'),
            ('profile_picture', 'VARCHAR(200)'),
            ('last_profile_update', 'DATETIME DEFAULT CURRENT_TIMESTAMP')
        ]
        
        # Add missing columns
        for column_name, column_type in new_columns:
            if column_name not in columns:
                try:
                    alter_sql = f"ALTER TABLE influencer ADD COLUMN {column_name} {column_type}"
                    db.session.execute(text(alter_sql))
                    print(f"✓ Added column: {column_name}")
                except Exception as e:
                    print(f"✗ Error adding column {column_name}: {e}")
        
        # Commit changes
        db.session.commit()
        print("✓ Database migration completed!")

if __name__ == "__main__":
    upgrade_database()
