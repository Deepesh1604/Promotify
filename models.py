from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Influencer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True, nullable=False)
    email = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(10), nullable=False)
    
    # Basic social media handles (existing - for backward compatibility)
    instagram = db.Column(db.String(15), unique=True, nullable=True)
    linkedin = db.Column(db.String(20), unique=True, nullable=True)
    twitter = db.Column(db.String(20), unique=True, nullable=True)
    youtube = db.Column(db.String(20), unique=True, nullable=True)
    
    # Enhanced Profile Information
    bio = db.Column(db.Text, nullable=True)
    niche = db.Column(db.String(100), nullable=True)  # Primary niche
    secondary_niches = db.Column(db.String(200), nullable=True)  # JSON string for multiple niches
    
    # Social Media Follower Counts
    instagram_followers = db.Column(db.Integer, default=0)
    youtube_subscribers = db.Column(db.Integer, default=0)
    twitter_followers = db.Column(db.Integer, default=0)
    linkedin_connections = db.Column(db.Integer, default=0)
    
    # Social Media URLs (full URLs instead of just handles)
    instagram_url = db.Column(db.String(200), nullable=True)
    youtube_url = db.Column(db.String(200), nullable=True)
    twitter_url = db.Column(db.String(200), nullable=True)
    linkedin_url = db.Column(db.String(200), nullable=True)
    
    # Profile Metrics
    engagement_rate = db.Column(db.Float, default=0.0)  # Average engagement rate
    profile_verified = db.Column(db.Boolean, default=False)
    profile_picture = db.Column(db.String(200), nullable=True)  # Path to profile picture
    last_profile_update = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Financial Information
    wallet_balance = db.Column(db.Float, default=0.0, nullable=False)
    bank_account = db.Column(db.String(20), nullable=True)
    ifsc_code = db.Column(db.String(11), nullable=True)
    
    # Timestamps
    date_joined = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    campaigns = db.relationship('Campaign', secondary='application', 
                                primaryjoin="and_(Influencer.id==Application.influencer_id, Application.status=='accepted')",
                                backref=db.backref('accepted_influencers', lazy='dynamic'))
    
    def get_total_followers(self):
        """Calculate total followers across all platforms"""
        return sum([
            self.instagram_followers or 0,
            self.youtube_subscribers or 0,
            self.twitter_followers or 0,
            self.linkedin_connections or 0
        ])
    
    def get_secondary_niches_list(self):
        """Get secondary niches as a list"""
        import json
        try:
            return json.loads(self.secondary_niches) if self.secondary_niches else []
        except:
            return []
    
    def set_secondary_niches_list(self, niches_list):
        """Set secondary niches from a list"""
        import json
        self.secondary_niches = json.dumps(niches_list) if niches_list else None

class Sponsor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True, nullable=False)
    email = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(10), nullable=False)
    industry = db.Column(db.String(20), nullable=False)
    wallet_balance = db.Column(db.Float, default=0.0, nullable=False)
    date_joined = db.Column(db.DateTime, default=datetime.utcnow)

class Campaign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sponsor_id = db.Column(db.Integer, db.ForeignKey('sponsor.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(15), nullable=False)
    description = db.Column(db.Text, nullable=True)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    budget = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    sponsor = db.relationship('Sponsor', backref=db.backref('campaigns', lazy=True, cascade='all, delete-orphan'))
    influencers = db.relationship('Influencer', secondary='application', 
                                  primaryjoin="and_(Campaign.id==Application.campaign_id, Application.status=='accepted')",
                                  backref=db.backref('accepted_campaigns', lazy='dynamic'))

    def __repr__(self):
        return f"Campaign('{self.name}')"

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    influencer_id = db.Column(db.Integer, db.ForeignKey('influencer.id', ondelete='CASCADE'), nullable=False)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id', ondelete='CASCADE'), nullable=False)
    status = db.Column(db.String(20), default='pending') 
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    influencer = db.relationship('Influencer', backref=db.backref('applications', lazy=True, cascade='all, delete-orphan'))
    campaign = db.relationship('Campaign', backref=db.backref('applications', lazy=True, cascade='all, delete-orphan'))

    def __repr__(self):
        return f"<Application {self.id}: {self.influencer.username} for {self.campaign.name}>"

class WalletTransaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)  # Sponsor or Influencer ID
    user_type = db.Column(db.String(20), nullable=False)  # 'sponsor' or 'influencer'
    transaction_type = db.Column(db.String(20), nullable=False)  # 'credit', 'debit', 'recharge', 'withdrawal'
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True)
    reference_id = db.Column(db.String(50), nullable=True)  # Campaign ID or Transaction reference
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<WalletTransaction {self.id}: {self.user_type} {self.user_id} - {self.transaction_type} ${self.amount}>"

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sponsor_id = db.Column(db.Integer, db.ForeignKey('sponsor.id', ondelete='CASCADE'), nullable=False)
    influencer_id = db.Column(db.Integer, db.ForeignKey('influencer.id', ondelete='CASCADE'), nullable=False)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id', ondelete='CASCADE'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')  # 'pending', 'completed', 'failed'
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    sponsor = db.relationship('Sponsor', backref=db.backref('payments_made', lazy=True))
    influencer = db.relationship('Influencer', backref=db.backref('payments_received', lazy=True))
    campaign = db.relationship('Campaign', backref=db.backref('payments', lazy=True))
    
    def __repr__(self):
        return f"<Payment {self.id}: {self.sponsor.username} -> {self.influencer.username} ${self.amount}>"

class CampaignInvitation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sponsor_id = db.Column(db.Integer, db.ForeignKey('sponsor.id', ondelete='CASCADE'), nullable=False)
    influencer_id = db.Column(db.Integer, db.ForeignKey('influencer.id', ondelete='CASCADE'), nullable=False)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id', ondelete='CASCADE'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # 'pending', 'accepted', 'declined'
    message = db.Column(db.Text, nullable=True)  # Optional invitation message from sponsor
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    responded_at = db.Column(db.DateTime, nullable=True)
    
    sponsor = db.relationship('Sponsor', backref=db.backref('invitations_sent', lazy=True))
    influencer = db.relationship('Influencer', backref=db.backref('invitations_received', lazy=True))
    campaign = db.relationship('Campaign', backref=db.backref('invitations', lazy=True))
    
    def __repr__(self):
        return f"<CampaignInvitation {self.id}: {self.sponsor.username} -> {self.influencer.username} for {self.campaign.name}>"
