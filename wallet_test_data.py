#!/usr/bin/env python3
"""
Test script to add wallet functionality and test data
"""

from main import app
from models import db, Sponsor, Influencer, WalletTransaction
import uuid

def setup_wallet_test_data():
    """Add initial wallet balances for testing"""
    with app.app_context():
        print("Setting up wallet test data...")
        
        # Find existing test users
        sponsor = Sponsor.query.filter_by(email='sponsor@test.com').first()
        influencer1 = Influencer.query.filter_by(email='tech@influencer.com').first()
        influencer2 = Influencer.query.filter_by(email='lifestyle@blogger.com').first()
        
        if sponsor:
            # Add initial balance to sponsor
            sponsor.wallet_balance = 100000.0  # ₹1,00,000
            
            # Create initial recharge transaction
            recharge_transaction = WalletTransaction(
                user_id=sponsor.id,
                user_type='sponsor',
                transaction_type='recharge',
                amount=100000.0,
                description='Initial wallet setup - Test recharge via UPI',
                reference_id=str(uuid.uuid4())[:8]
            )
            db.session.add(recharge_transaction)
            print(f"✅ Added ₹1,00,000 to sponsor wallet")
        
        if influencer1:
            # Add some initial earnings
            influencer1.wallet_balance = 15000.0  # ₹15,000
            influencer1.bank_account = '1234567890'
            influencer1.ifsc_code = 'HDFC0001234'
            
            earning_transaction = WalletTransaction(
                user_id=influencer1.id,
                user_type='influencer',
                transaction_type='credit',
                amount=15000.0,
                description='Earnings from completed campaign - Tech Product Launch',
                reference_id='campaign_test_1'
            )
            db.session.add(earning_transaction)
            print(f"✅ Added ₹15,000 to {influencer1.username} wallet")
        
        if influencer2:
            # Add some initial earnings
            influencer2.wallet_balance = 8500.0  # ₹8,500
            influencer2.bank_account = '9876543210'
            influencer2.ifsc_code = 'SBI0001234'
            
            earning_transaction = WalletTransaction(
                user_id=influencer2.id,
                user_type='influencer',
                transaction_type='credit',
                amount=8500.0,
                description='Earnings from completed campaign - Summer Collection',
                reference_id='campaign_test_2'
            )
            db.session.add(earning_transaction)
            print(f"✅ Added ₹8,500 to {influencer2.username} wallet")
        
        db.session.commit()
        
        print("\n💰 Wallet Test Data Summary:")
        if sponsor:
            print(f"   - Sponsor ({sponsor.username}): ₹{sponsor.wallet_balance:,.2f}")
        if influencer1:
            print(f"   - Influencer 1 ({influencer1.username}): ₹{influencer1.wallet_balance:,.2f}")
        if influencer2:
            print(f"   - Influencer 2 ({influencer2.username}): ₹{influencer2.wallet_balance:,.2f}")
        
        print("\n🔐 Test the wallet functionality:")
        print("   1. Login as sponsor: sponsor@test.com / password123")
        print("   2. Go to Wallet page and try accepting campaign applications")
        print("   3. Login as influencer and check wallet balance")
        print("   4. Try withdrawing funds to bank account")

if __name__ == "__main__":
    setup_wallet_test_data()
