from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Influencer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True, nullable=False)
    email = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(10), nullable=False)
    instagram = db.Column(db.String(15), unique=True, nullable=True)
    linkedin = db.Column(db.String(20), unique=True, nullable=True)
    twitter = db.Column(db.String(20), unique=True, nullable=True)
    youtube = db.Column(db.String(20), unique=True, nullable=True)
    wallet_balance = db.Column(db.Float, default=0.0, nullable=False)
    bank_account = db.Column(db.String(20), nullable=True)
    ifsc_code = db.Column(db.String(11), nullable=True)
    date_joined = db.Column(db.DateTime, default=datetime.utcnow)
    campaigns = db.relationship('Campaign', secondary='application', 
                                primaryjoin="and_(Influencer.id==Application.influencer_id, Application.status=='accepted')",
                                backref=db.backref('accepted_influencers', lazy='dynamic'))

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
