from flask import render_template, redirect, url_for, request, flash, session, make_response
from models import db, Influencer, Sponsor, Campaign, Application, WalletTransaction, Payment
from datetime import datetime, timedelta
from sqlalchemy import func, or_
import sqlalchemy
import json
import uuid

ADMIN_EMAIL = 'admin@gmail.com'
ADMIN_PASSWORD = 'admin123'

def register_routes(app):
    
    @app.route('/')
    def index():
        return render_template('home.html')

    @app.route('/slogin', methods=['GET', 'POST'])
    def spon_log():
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']
            sponsor = Sponsor.query.filter_by(email=email, password=password).first()
            if sponsor:
                session['sponsor_logged_in'] = True
                session['sponsor_id'] = sponsor.id
                return redirect(url_for('spon_dash'))
            else:
                flash('Invalid email or password', 'error')
                return redirect(url_for('spon_log'))
        return render_template('spon_log.html')

    @app.route('/slogout')
    def spon_logout():
        session.pop('sponsor_logged_in', None)
        session.pop('sponsor_id', None)
        flash('You have been logged out.', 'success')
        return redirect(url_for('spon_log'))

    @app.route('/sreg', methods=['GET', 'POST'])
    def spon_reg():
        if request.method == 'POST':
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            industry = request.form['industry']
            
            existing_sponsor = Sponsor.query.filter((Sponsor.email == email) | (Sponsor.username == username)).first()
            if existing_sponsor:
                flash('Email or Username already exists', 'error')
                return redirect(url_for('spon_reg'))
            
            new_sponsor = Sponsor(username=username, email=email, password=password, industry=industry)
            db.session.add(new_sponsor)
            db.session.commit()
            flash('Sponsor account created successfully!', 'success')
            return redirect(url_for('spon_log'))

        return render_template('spon_reg.html')

    @app.route('/ilogin', methods=['GET', 'POST'])
    def influ_log():
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']
            influencer = Influencer.query.filter_by(email=email, password=password).first()
            if influencer:
                session['influencer_logged_in'] = True
                session['influencer_id'] = influencer.id
                return redirect(url_for('influ_dash'))
            else:
                flash('Invalid email or password', 'error')
                return redirect(url_for('influ_log'))
        return render_template('influ_log.html')

    @app.route('/ireg', methods=['GET', 'POST'])
    def influ_reg():
        if request.method == 'POST':
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            instagram = request.form['instagram']
            linkedin = request.form['linkedin']
            twitter = request.form['twitter']
            youtube = request.form['youtube']
            existing_influencer = Influencer.query.filter((Influencer.email == email) | (Influencer.username == username)).first()
            if existing_influencer:
                flash('Email or Username already exists', 'error')
                return redirect(url_for('influ_reg'))
            
            new_influencer = Influencer(username=username, email=email, password=password, instagram=instagram, linkedin=linkedin, twitter=twitter, youtube=youtube )
            db.session.add(new_influencer)
            db.session.commit()
            flash('Influencer account created successfully!', 'success')
            return redirect(url_for('influ_log'))

        return render_template('influ_reg.html')

    @app.route('/idash')
    @app.route('/idash/<int:campaign_id>')
    def influ_dash(campaign_id=None):
        if 'influencer_id' not in session:
            flash('You need to log in first.', 'error')
            return redirect(url_for('influ_log'))

        influencer = Influencer.query.get(session['influencer_id'])
        
        # Get pagination parameters from query string
        pending_limit = int(request.args.get('pending_limit', 10))
        active_limit = int(request.args.get('active_limit', 10))
        available_limit = int(request.args.get('available_limit', 10))
        
        # Get campaigns that influencer hasn't applied to or been accepted into
        applied_campaign_ids = [app.campaign_id for app in influencer.applications]
        all_available_campaigns = Campaign.query.filter(
            ~Campaign.id.in_(applied_campaign_ids),
            Campaign.end_date >= datetime.now().date()
        ).order_by(Campaign.start_date.desc()).all()
        
        # Get pending applications
        all_pending_applications = Application.query.filter_by(
            influencer_id=influencer.id, 
            status='pending'
        ).order_by(Application.created_at.desc()).all()
        
        # Get accepted/active campaigns
        all_active_campaigns = Application.query.filter_by(
            influencer_id=influencer.id, 
            status='accepted'
        ).order_by(Application.created_at.desc()).all()
        
        # Paginate results
        available_campaigns = all_available_campaigns[:available_limit]
        pending_applications = all_pending_applications[:pending_limit]
        active_campaigns = all_active_campaigns[:active_limit]
        
        # Calculate if there are more items to show
        has_more_available = len(all_available_campaigns) > available_limit
        has_more_pending = len(all_pending_applications) > pending_limit
        has_more_active = len(all_active_campaigns) > active_limit
        
        selected_campaign = None
        if campaign_id:
            selected_campaign = Campaign.query.get(campaign_id)
        
        return render_template('influ_dash.html', 
                               influencer=influencer, 
                               available_campaigns=available_campaigns,
                               pending_applications=pending_applications,
                               active_campaigns=active_campaigns,
                               selected_campaign=selected_campaign,
                               has_more_available=has_more_available,
                               has_more_pending=has_more_pending,
                               has_more_active=has_more_active,
                               available_limit=available_limit,
                               pending_limit=pending_limit,
                               active_limit=active_limit,
                               total_available=len(all_available_campaigns),
                               total_pending=len(all_pending_applications),
                               total_active=len(all_active_campaigns))

    @app.route('/ilogout')
    def influ_logout():
        session.pop('influencer_id', None)
        return redirect(url_for('influ_log'))

    @app.route('/adash')
    def admin_dash():
        if 'admin_logged_in' not in session or not session['admin_logged_in']:
            flash('You need to log in first.', 'error')
            return redirect(url_for('admin_log'))

        search_query = request.args.get('search', '')

        # Query all campaigns
        campaigns_query = Campaign.query

        if search_query:
            search_filter = or_(
                Campaign.name.ilike(f'%{search_query}%'),
                Campaign.sponsor.has(Sponsor.username.ilike(f'%{search_query}%'))
            )
            campaigns_query = campaigns_query.filter(search_filter)

        campaigns = campaigns_query.order_by(Campaign.start_date.desc()).all()

        for campaign in campaigns:
            if campaign.start_date <= datetime.utcnow().date() <= campaign.end_date:
                campaign.status = "Ongoing"
            elif campaign.start_date > datetime.utcnow().date():
                campaign.status = "Upcoming"
            else:
                campaign.status = "Completed"

            total_days = (campaign.end_date - campaign.start_date).days
            days_passed = (datetime.utcnow().date() - campaign.start_date).days
            campaign.progress = min(max(int((days_passed / total_days) * 100), 0), 100)

        # Calculate stats
        total_users = Influencer.query.count() + Sponsor.query.count()
        total_influencers = Influencer.query.count()
        total_sponsors = Sponsor.query.count()
        total_campaigns = Campaign.query.count()
        active_campaigns = Campaign.query.filter(
            Campaign.start_date <= datetime.utcnow().date(),
            Campaign.end_date >= datetime.utcnow().date()
        ).count()

        stats = {
            'total_users': total_users,
            'total_influencers': total_influencers,
            'total_sponsors': total_sponsors,
            'total_campaigns': total_campaigns,
            'active_campaigns': active_campaigns
        }

        return render_template('admin_dash.html', 
                               campaigns=campaigns,
                               search_query=search_query,
                               stats=stats)

    @app.route('/alogin', methods=['GET', 'POST'])
    def admin_log():
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']
            
            if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
                session['admin_logged_in'] = True
                flash('Logged in successfully', 'success')
                return redirect(url_for('admin_dash'))
            else:
                flash('Invalid credentials', 'error')
                return redirect(url_for('admin_log'))

        return render_template('admin_log.html')

    @app.route('/alogout')
    def admin_logout():
        session.pop('admin_logged_in', None)
        flash('You have been logged out.', 'success')
        return redirect(url_for('admin_log'))

    @app.route('/afind')
    def afind():
        if 'admin_logged_in' not in session or not session['admin_logged_in']:
            flash('You need to log in first.', 'error')
            return redirect(url_for('admin_log'))

        search_query = request.args.get('search', '')
        filter_options = request.args.getlist('filter')
        
        sponsors = []
        influencers = []
        campaigns = []

        if 'sponsors' in filter_options or not filter_options:
            sponsors = Sponsor.query.filter(Sponsor.username.contains(search_query)).all()

        if 'influencers' in filter_options or not filter_options:
            influencers = Influencer.query.filter(Influencer.username.contains(search_query)).all()

        if 'campaigns' in filter_options or not filter_options:
            campaigns = Campaign.query.filter(Campaign.name.contains(search_query)).all()
        
        return render_template('afind.html', 
                               sponsors=sponsors, 
                               influencers=influencers, 
                               campaigns=campaigns, 
                               search_query=search_query, 
                               filter_options=filter_options)

    @app.route('/remove_sponsor/<int:sponsor_id>', methods=['POST'])
    def remove_sponsor(sponsor_id):
        if 'admin_logged_in' not in session or not session['admin_logged_in']:
            flash('You need to log in first.', 'error')
            return redirect(url_for('admin_log'))

        sponsor = Sponsor.query.get_or_404(sponsor_id)
        db.session.delete(sponsor)
        db.session.commit()
        flash(f'Sponsor "{sponsor.username}" has been removed.', 'success')
        
        search_query = request.args.get('search', '')
        filter_options = request.args.getlist('filter')
        return redirect(url_for('afind', search=search_query, filter=filter_options))

    @app.route('/remove_influencer/<int:influencer_id>', methods=['POST'])
    def remove_influencer(influencer_id):
        if 'admin_logged_in' not in session or not session['admin_logged_in']:
            flash('You need to log in first.', 'error')
            return redirect(url_for('admin_log'))

        influencer = Influencer.query.get_or_404(influencer_id)
        db.session.delete(influencer)
        db.session.commit()
        flash(f'Influencer "{influencer.username}" has been removed.', 'success')
        
        search_query = request.args.get('search', '')
        filter_options = request.args.getlist('filter')
        return redirect(url_for('afind', search=search_query, filter=filter_options))

    @app.route('/remove_campaign/<int:campaign_id>', methods=['POST'])
    def remove_campaign(campaign_id):
        if 'admin_logged_in' not in session or not session['admin_logged_in']:
            flash('You need to log in first.', 'error')
            return redirect(url_for('admin_log'))

        try:
            campaign = Campaign.query.get_or_404(campaign_id)
            campaign_name = campaign.name
            
            # First, delete all applications related to this campaign
            applications = Application.query.filter_by(campaign_id=campaign_id).all()
            for application in applications:
                db.session.delete(application)
            
            # Flush the session to ensure applications are deleted before deleting campaign
            db.session.flush()
            
            # Now delete the campaign
            db.session.delete(campaign)
            db.session.commit()
            
            flash(f'Campaign "{campaign_name}" has been removed successfully.', 'success')
            
        except Exception as e:
            db.session.rollback()
            flash('There was an error removing the campaign. Please try again.', 'error')
            print(f"Error removing campaign: {e}")  # For debugging
        
        search_query = request.args.get('search', '')
        filter_options = request.args.getlist('filter')
        return redirect(url_for('afind', search=search_query, filter=filter_options))

    def get_user_growth_data():
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=180)  # Last 6 months
        
        new_users = db.session.query(
            func.strftime('%Y-%m', Influencer.date_joined).label('month'),
            func.count(Influencer.id).label('count')
        ).filter(Influencer.date_joined >= start_date).group_by('month').all()
        
        new_users += db.session.query(
            func.strftime('%Y-%m', Sponsor.date_joined).label('month'),
            func.count(Sponsor.id).label('count')
        ).filter(Sponsor.date_joined >= start_date).group_by('month').all()
        
        # Process the data into the format needed for the chart
        months = [start_date + timedelta(days=30*i) for i in range(6)]
        new_user_data = [sum(nu.count for nu in new_users if nu.month == month.strftime('%Y-%m')) for month in months]
        
        return {
            'labels': [month.strftime('%b') for month in months],
            'new_users': new_user_data,
        }

    def get_user_distribution():
        influencer_count = Influencer.query.count()
        sponsor_count = Sponsor.query.count()
        
        return {
            'labels': ['Influencers', 'Sponsors'],
            'data': [influencer_count, sponsor_count]
        }

    def get_campaign_count():
        active_count = Campaign.query.filter(
            Campaign.start_date <= datetime.utcnow(),
            Campaign.end_date >= datetime.utcnow()
        ).count()
        completed_count = Campaign.query.filter(
            Campaign.end_date < datetime.utcnow()
        ).count()
        upcoming_count = Campaign.query.filter(
            Campaign.start_date > datetime.utcnow()
        ).count()
        
        return {
            'labels': ['Active', 'Completed', 'Upcoming'],
            'data': [active_count, completed_count, upcoming_count]
        }

    def get_top_industries():
        top_industries = db.session.query(
            Sponsor.industry, 
            func.count(Sponsor.id).label('count')
        ).group_by(Sponsor.industry).order_by(func.count(Sponsor.id).desc()).limit(5).all()
        
        return {
            'labels': [industry for industry, _ in top_industries],
            'data': [count for _, count in top_industries]
        }

    def get_campaign_budget_distribution():
        # Get budget ranges
        low_budget = Campaign.query.filter(Campaign.budget < 10000).count()
        mid_budget = Campaign.query.filter(Campaign.budget >= 10000, Campaign.budget < 50000).count()
        high_budget = Campaign.query.filter(Campaign.budget >= 50000, Campaign.budget < 100000).count()
        premium_budget = Campaign.query.filter(Campaign.budget >= 100000).count()
        
        return {
            'labels': ['< $10K', '$10K - $50K', '$50K - $100K', '$100K+'],
            'data': [low_budget, mid_budget, high_budget, premium_budget]
        }

    def get_monthly_registrations():
        # Get user registrations by month for the last 6 months
        months = []
        influencer_data = []
        sponsor_data = []
        
        for i in range(5, -1, -1):
            date = datetime.utcnow() - timedelta(days=30*i)
            month_start = date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if i > 0:
                next_month = (date.replace(day=28) + timedelta(days=4)).replace(day=1)
            else:
                next_month = datetime.utcnow()
            
            month_name = month_start.strftime('%b %Y')
            months.append(month_name)
            
            # Count influencers registered in this month
            inf_count = Influencer.query.filter(
                Influencer.date_joined >= month_start,
                Influencer.date_joined < next_month
            ).count()
            
            # Count sponsors registered in this month
            spon_count = Sponsor.query.filter(
                Sponsor.date_joined >= month_start,
                Sponsor.date_joined < next_month
            ).count()
            
            influencer_data.append(inf_count)
            sponsor_data.append(spon_count)
        
        return {
            'labels': months,
            'influencer_data': influencer_data,
            'sponsor_data': sponsor_data
        }

    def get_application_status_distribution():
        pending_apps = Application.query.filter_by(status='pending').count()
        accepted_apps = Application.query.filter_by(status='accepted').count()
        rejected_apps = Application.query.filter_by(status='rejected').count()
        
        return {
            'labels': ['Pending', 'Accepted', 'Rejected'],
            'data': [pending_apps, accepted_apps, rejected_apps]
        }

    def get_campaign_duration_analysis():
        # Analyze campaign durations
        short_campaigns = Campaign.query.filter(
            func.julianday(Campaign.end_date) - func.julianday(Campaign.start_date) <= 30
        ).count()
        
        medium_campaigns = Campaign.query.filter(
            func.julianday(Campaign.end_date) - func.julianday(Campaign.start_date) > 30,
            func.julianday(Campaign.end_date) - func.julianday(Campaign.start_date) <= 90
        ).count()
        
        long_campaigns = Campaign.query.filter(
            func.julianday(Campaign.end_date) - func.julianday(Campaign.start_date) > 90
        ).count()
        
        return {
            'labels': ['Short (≤30 days)', 'Medium (31-90 days)', 'Long (>90 days)'],
            'data': [short_campaigns, medium_campaigns, long_campaigns]
        }

    def get_influencer_engagement_stats():
        # Get stats about influencer social media presence
        instagram_users = Influencer.query.filter(Influencer.instagram.isnot(None), Influencer.instagram != '').count()
        twitter_users = Influencer.query.filter(Influencer.twitter.isnot(None), Influencer.twitter != '').count()
        youtube_users = Influencer.query.filter(Influencer.youtube.isnot(None), Influencer.youtube != '').count()
        linkedin_users = Influencer.query.filter(Influencer.linkedin.isnot(None), Influencer.linkedin != '').count()
        
        return {
            'labels': ['Instagram', 'Twitter', 'YouTube', 'LinkedIn'],
            'data': [instagram_users, twitter_users, youtube_users, linkedin_users]
        }

    @app.route('/ahistory')
    def admin_history():
        if 'admin_logged_in' not in session or not session['admin_logged_in']:
            flash('You need to log in first.', 'error')
            return redirect(url_for('admin_log'))
        
        filter_type = request.args.get('filter', 'overall')
        search_query = request.args.get('search', '')
        user_filter = request.args.get('user_filter', 'all')  # all, sponsors, influencers
        
        # Calculate date ranges
        now = datetime.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = now - timedelta(days=7)
        month_start = now - timedelta(days=30)
        
        # Base queries for all platform data
        applications_query = Application.query
        campaigns_query = Campaign.query
        transactions_query = WalletTransaction.query
        payments_query = Payment.query
        sponsors_query = Sponsor.query
        influencers_query = Influencer.query
        
        # Apply date filters
        if filter_type == 'today':
            applications = applications_query.filter(Application.created_at >= today_start)
            campaigns = campaigns_query.filter(Campaign.created_at >= today_start)
            transactions = transactions_query.filter(WalletTransaction.created_at >= today_start)
            payments = payments_query.filter(Payment.payment_date >= today_start)
            sponsors = sponsors_query.filter(Sponsor.date_joined >= today_start.date())
            influencers = influencers_query.filter(Influencer.date_joined >= today_start.date())
            title = "Today's Platform Activity"
        elif filter_type == 'week':
            applications = applications_query.filter(Application.created_at >= week_start)
            campaigns = campaigns_query.filter(Campaign.created_at >= week_start)
            transactions = transactions_query.filter(WalletTransaction.created_at >= week_start)
            payments = payments_query.filter(Payment.payment_date >= week_start)
            sponsors = sponsors_query.filter(Sponsor.date_joined >= week_start.date())
            influencers = influencers_query.filter(Influencer.date_joined >= week_start.date())
            title = "Last Week's Platform Activity"
        elif filter_type == 'month':
            applications = applications_query.filter(Application.created_at >= month_start)
            campaigns = campaigns_query.filter(Campaign.created_at >= month_start)
            transactions = transactions_query.filter(WalletTransaction.created_at >= month_start)
            payments = payments_query.filter(Payment.payment_date >= month_start)
            sponsors = sponsors_query.filter(Sponsor.date_joined >= month_start.date())
            influencers = influencers_query.filter(Influencer.date_joined >= month_start.date())
            title = "Last Month's Platform Activity"
        else:  # overall
            applications = applications_query
            campaigns = campaigns_query
            transactions = transactions_query
            payments = payments_query
            sponsors = sponsors_query
            influencers = influencers_query
            title = "Complete Platform History"
        
        # Apply search filters
        if search_query:
            # Search in campaigns
            campaigns = campaigns.filter(
                or_(
                    Campaign.name.ilike(f'%{search_query}%'),
                    Campaign.sponsor.has(Sponsor.username.ilike(f'%{search_query}%'))
                )
            )
            
            # Search in applications
            applications = applications.filter(
                or_(
                    Application.campaign.has(Campaign.name.ilike(f'%{search_query}%')),
                    Application.influencer.has(Influencer.username.ilike(f'%{search_query}%')),
                    Application.campaign.has(Campaign.sponsor.has(Sponsor.username.ilike(f'%{search_query}%')))
                )
            )
            
            # Search in transactions
            transactions = transactions.filter(
                WalletTransaction.description.ilike(f'%{search_query}%')
            )
            
            # Search in users
            sponsors = sponsors.filter(
                or_(
                    Sponsor.username.ilike(f'%{search_query}%'),
                    Sponsor.email.ilike(f'%{search_query}%')
                )
            )
            
            influencers = influencers.filter(
                or_(
                    Influencer.username.ilike(f'%{search_query}%'),
                    Influencer.email.ilike(f'%{search_query}%')
                )
            )
        
        # Apply user filter
        if user_filter == 'sponsors':
            influencers = influencers.filter(False)  # Empty query
            applications = applications.filter(False)
            transactions = transactions.filter(WalletTransaction.user_type == 'sponsor')
        elif user_filter == 'influencers':
            sponsors = sponsors.filter(False)  # Empty query
            campaigns = campaigns.filter(False)
            transactions = transactions.filter(WalletTransaction.user_type == 'influencer')
        
        # Execute queries and order results
        applications = applications.order_by(Application.created_at.desc()).all()
        campaigns = campaigns.order_by(Campaign.created_at.desc()).all()
        transactions = transactions.order_by(WalletTransaction.created_at.desc()).all()
        payments = payments.order_by(Payment.payment_date.desc()).all()
        sponsors = sponsors.order_by(Sponsor.date_joined.desc()).all()
        influencers = influencers.order_by(Influencer.date_joined.desc()).all()
        
        # Calculate comprehensive summary statistics
        total_revenue = sum(t.amount for t in transactions if t.transaction_type == 'debit')
        total_payouts = sum(t.amount for t in transactions if t.transaction_type == 'credit')
        total_recharges = sum(t.amount for t in transactions if t.transaction_type == 'recharge')
        total_withdrawals = sum(t.amount for t in transactions if t.transaction_type == 'withdrawal')
        
        total_applications = len(applications)
        accepted_applications = len([app for app in applications if app.status == 'accepted'])
        pending_applications = len([app for app in applications if app.status == 'pending'])
        rejected_applications = len([app for app in applications if app.status == 'rejected'])
        
        total_campaigns = len(campaigns)
        active_campaigns = len([c for c in campaigns if c.start_date <= now.date() <= c.end_date])
        completed_campaigns = len([c for c in campaigns if c.end_date < now.date()])
        
        total_users = len(sponsors) + len(influencers)
        total_sponsors = len(sponsors)
        total_influencers = len(influencers)
        
        total_payments = len(payments)
        completed_payments = len([p for p in payments if p.status == 'completed'])
        
        summary = {
            'total_revenue': total_revenue,
            'total_payouts': total_payouts,
            'total_recharges': total_recharges,
            'total_withdrawals': total_withdrawals,
            'total_applications': total_applications,
            'accepted_applications': accepted_applications,
            'pending_applications': pending_applications,
            'rejected_applications': rejected_applications,
            'total_campaigns': total_campaigns,
            'active_campaigns': active_campaigns,
            'completed_campaigns': completed_campaigns,
            'total_users': total_users,
            'total_sponsors': total_sponsors,
            'total_influencers': total_influencers,
            'total_payments': total_payments,
            'completed_payments': completed_payments
        }
        
        return render_template('admin_history.html',
                               applications=applications,
                               campaigns=campaigns,
                               transactions=transactions,
                               payments=payments,
                               sponsors=sponsors,
                               influencers=influencers,
                               filter_type=filter_type,
                               search_query=search_query,
                               user_filter=user_filter,
                               title=title,
                               summary=summary,
                               current_date=now.date())

    @app.route('/ahistory/download')
    def download_admin_history():
        if 'admin_logged_in' not in session or not session['admin_logged_in']:
            flash('You need to log in first.', 'error')
            return redirect(url_for('admin_log'))
        
        filter_type = request.args.get('filter', 'overall')
        search_query = request.args.get('search', '')
        user_filter = request.args.get('user_filter', 'all')
        history_type = request.args.get('type', 'all')
        
        # Calculate date ranges (same as history route)
        now = datetime.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = now - timedelta(days=7)
        month_start = now - timedelta(days=30)
        
        # Base queries
        applications_query = Application.query
        campaigns_query = Campaign.query
        transactions_query = WalletTransaction.query
        payments_query = Payment.query
        sponsors_query = Sponsor.query
        influencers_query = Influencer.query
        
        # Apply date filters (same logic as history route)
        if filter_type == 'today':
            applications = applications_query.filter(Application.created_at >= today_start)
            campaigns = campaigns_query.filter(Campaign.created_at >= today_start)
            transactions = transactions_query.filter(WalletTransaction.created_at >= today_start)
            payments = payments_query.filter(Payment.payment_date >= today_start)
            sponsors = sponsors_query.filter(Sponsor.date_joined >= today_start.date())
            influencers = influencers_query.filter(Influencer.date_joined >= today_start.date())
            period_suffix = "today"
        elif filter_type == 'week':
            applications = applications_query.filter(Application.created_at >= week_start)
            campaigns = campaigns_query.filter(Campaign.created_at >= week_start)
            transactions = transactions_query.filter(WalletTransaction.created_at >= week_start)
            payments = payments_query.filter(Payment.payment_date >= week_start)
            sponsors = sponsors_query.filter(Sponsor.date_joined >= week_start.date())
            influencers = influencers_query.filter(Influencer.date_joined >= week_start.date())
            period_suffix = "week"
        elif filter_type == 'month':
            applications = applications_query.filter(Application.created_at >= month_start)
            campaigns = campaigns_query.filter(Campaign.created_at >= month_start)
            transactions = transactions_query.filter(WalletTransaction.created_at >= month_start)
            payments = payments_query.filter(Payment.payment_date >= month_start)
            sponsors = sponsors_query.filter(Sponsor.date_joined >= month_start.date())
            influencers = influencers_query.filter(Influencer.date_joined >= month_start.date())
            period_suffix = "month"
        else:  # overall
            applications = applications_query
            campaigns = campaigns_query
            transactions = transactions_query
            payments = payments_query
            sponsors = sponsors_query
            influencers = influencers_query
            period_suffix = "overall"
        
        # Apply search and user filters (same as history route)
        if search_query:
            campaigns = campaigns.filter(
                or_(
                    Campaign.name.ilike(f'%{search_query}%'),
                    Campaign.sponsor.has(Sponsor.username.ilike(f'%{search_query}%'))
                )
            )
            applications = applications.filter(
                or_(
                    Application.campaign.has(Campaign.name.ilike(f'%{search_query}%')),
                    Application.influencer.has(Influencer.username.ilike(f'%{search_query}%')),
                    Application.campaign.has(Campaign.sponsor.has(Sponsor.username.ilike(f'%{search_query}%')))
                )
            )
            transactions = transactions.filter(WalletTransaction.description.ilike(f'%{search_query}%'))
            sponsors = sponsors.filter(
                or_(
                    Sponsor.username.ilike(f'%{search_query}%'),
                    Sponsor.email.ilike(f'%{search_query}%')
                )
            )
            influencers = influencers.filter(
                or_(
                    Influencer.username.ilike(f'%{search_query}%'),
                    Influencer.email.ilike(f'%{search_query}%')
                )
            )
        
        if user_filter == 'sponsors':
            influencers = influencers.filter(False)
            applications = applications.filter(False)
            transactions = transactions.filter(WalletTransaction.user_type == 'sponsor')
        elif user_filter == 'influencers':
            sponsors = sponsors.filter(False)
            campaigns = campaigns.filter(False)
            transactions = transactions.filter(WalletTransaction.user_type == 'influencer')
        
        # Execute queries
        applications = applications.order_by(Application.created_at.desc()).all()
        campaigns = campaigns.order_by(Campaign.created_at.desc()).all()
        transactions = transactions.order_by(WalletTransaction.created_at.desc()).all()
        payments = payments.order_by(Payment.payment_date.desc()).all()
        sponsors = sponsors.order_by(Sponsor.date_joined.desc()).all()
        influencers = influencers.order_by(Influencer.date_joined.desc()).all()
        
        # Apply history type filter
        if history_type == 'applications':
            campaigns = []
            transactions = []
            payments = []
            sponsors = []
            influencers = []
            type_suffix = "applications"
        elif history_type == 'campaigns':
            applications = []
            transactions = []
            payments = []
            sponsors = []
            influencers = []
            type_suffix = "campaigns"
        elif history_type == 'transactions':
            applications = []
            campaigns = []
            payments = []
            sponsors = []
            influencers = []
            type_suffix = "transactions"
        elif history_type == 'payments':
            applications = []
            campaigns = []
            transactions = []
            sponsors = []
            influencers = []
            type_suffix = "payments"
        elif history_type == 'users':
            applications = []
            campaigns = []
            transactions = []
            payments = []
            type_suffix = "users"
        else:  # all
            type_suffix = "all"
        
        # Generate filename
        search_suffix = f"_{search_query}" if search_query else ""
        user_suffix = f"_{user_filter}" if user_filter != 'all' else ""
        filename = f"admin_history_{period_suffix}_{type_suffix}{user_suffix}{search_suffix}_{now.strftime('%Y%m%d')}.csv"
        
        # Create CSV content
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write comprehensive headers based on history type
        if history_type == 'applications':
            writer.writerow(['Application Date', 'Campaign', 'Sponsor', 'Influencer', 'Budget', 'Status'])
        elif history_type == 'campaigns':
            writer.writerow(['Creation Date', 'Campaign Name', 'Sponsor', 'Start Date', 'End Date', 'Budget', 'Description'])
        elif history_type == 'transactions':
            writer.writerow(['Date', 'User Type', 'Username', 'Transaction Type', 'Amount', 'Description', 'Reference'])
        elif history_type == 'payments':
            writer.writerow(['Payment Date', 'Campaign', 'Sponsor', 'Influencer', 'Amount', 'Status'])
        elif history_type == 'users':
            writer.writerow(['Join Date', 'User Type', 'Username', 'Email', 'Additional Info'])
        else:  # all types
            writer.writerow(['Type', 'Date', 'Primary Info', 'Secondary Info', 'Amount', 'Status', 'Description'])
        
        # Write data based on type
        all_data = []
        
        # Applications data
        for application in applications:
            if history_type in ['applications', 'all']:
                if history_type == 'applications':
                    writer.writerow([
                        application.created_at.strftime('%Y-%m-%d %H:%M'),
                        application.campaign.name,
                        application.campaign.sponsor.username,
                        application.influencer.username,
                        f"₹{application.campaign.budget:.2f}",
                        application.status.title()
                    ])
                else:
                    all_data.append([
                        'Application',
                        application.created_at.strftime('%Y-%m-%d %H:%M'),
                        f"{application.influencer.username} → {application.campaign.name}",
                        f"Sponsor: {application.campaign.sponsor.username}",
                        f"₹{application.campaign.budget:.2f}",
                        application.status.title(),
                        f"Application for campaign {application.campaign.name}"
                    ])
        
        # Campaign data
        for campaign in campaigns:
            if history_type in ['campaigns', 'all']:
                if history_type == 'campaigns':
                    writer.writerow([
                        campaign.created_at.strftime('%Y-%m-%d %H:%M'),
                        campaign.name,
                        campaign.sponsor.username,
                        campaign.start_date.strftime('%Y-%m-%d'),
                        campaign.end_date.strftime('%Y-%m-%d'),
                        f"₹{campaign.budget:.2f}",
                        campaign.description[:100] + '...' if len(campaign.description) > 100 else campaign.description
                    ])
                else:
                    all_data.append([
                        'Campaign',
                        campaign.created_at.strftime('%Y-%m-%d %H:%M'),
                        campaign.name,
                        f"By: {campaign.sponsor.username}",
                        f"₹{campaign.budget:.2f}",
                        f"{campaign.start_date} to {campaign.end_date}",
                        campaign.description[:100] + '...' if len(campaign.description) > 100 else campaign.description
                    ])
        
        # Transaction data
        for transaction in transactions:
            if history_type in ['transactions', 'all']:
                user = None
                if transaction.user_type == 'sponsor':
                    user = Sponsor.query.get(transaction.user_id)
                elif transaction.user_type == 'influencer':
                    user = Influencer.query.get(transaction.user_id)
                
                username = user.username if user else f"Unknown {transaction.user_type}"
                
                if history_type == 'transactions':
                    writer.writerow([
                        transaction.created_at.strftime('%Y-%m-%d %H:%M'),
                        transaction.user_type.title(),
                        username,
                        transaction.transaction_type.title(),
                        f"₹{transaction.amount:.2f}",
                        transaction.description,
                        transaction.reference_id or 'N/A'
                    ])
                else:
                    all_data.append([
                        'Transaction',
                        transaction.created_at.strftime('%Y-%m-%d %H:%M'),
                        f"{transaction.transaction_type.title()} by {username}",
                        f"User: {transaction.user_type.title()}",
                        f"₹{transaction.amount:.2f}",
                        'Completed',
                        transaction.description
                    ])
        
        # Payment data
        for payment in payments:
            if history_type in ['payments', 'all']:
                if history_type == 'payments':
                    writer.writerow([
                        payment.payment_date.strftime('%Y-%m-%d %H:%M'),
                        payment.campaign.name,
                        payment.sponsor.username,
                        payment.influencer.username,
                        f"₹{payment.amount:.2f}",
                        payment.status.title()
                    ])
                else:
                    all_data.append([
                        'Payment',
                        payment.payment_date.strftime('%Y-%m-%d %H:%M'),
                        f"{payment.sponsor.username} → {payment.influencer.username}",
                        f"Campaign: {payment.campaign.name}",
                        f"₹{payment.amount:.2f}",
                        payment.status.title(),
                        f"Payment for campaign {payment.campaign.name}"
                    ])
        
        # User registration data
        for sponsor in sponsors:
            if history_type in ['users', 'all']:
                if history_type == 'users':
                    writer.writerow([
                        sponsor.date_joined.strftime('%Y-%m-%d'),
                        'Sponsor',
                        sponsor.username,
                        sponsor.email,
                        f"Industry: {sponsor.industry}"
                    ])
                else:
                    all_data.append([
                        'User Registration',
                        sponsor.date_joined.strftime('%Y-%m-%d'),
                        f"Sponsor: {sponsor.username}",
                        sponsor.email,
                        '-',
                        'Registered',
                        f"New sponsor registered - Industry: {sponsor.industry}"
                    ])
        
        for influencer in influencers:
            if history_type in ['users', 'all']:
                platforms = []
                if influencer.instagram: platforms.append('Instagram')
                if influencer.twitter: platforms.append('Twitter')
                if influencer.youtube: platforms.append('YouTube')
                if influencer.linkedin: platforms.append('LinkedIn')
                
                if history_type == 'users':
                    writer.writerow([
                        influencer.date_joined.strftime('%Y-%m-%d'),
                        'Influencer',
                        influencer.username,
                        influencer.email,
                        f"Platforms: {', '.join(platforms) if platforms else 'None'}"
                    ])
                else:
                    all_data.append([
                        'User Registration',
                        influencer.date_joined.strftime('%Y-%m-%d'),
                        f"Influencer: {influencer.username}",
                        influencer.email,
                        '-',
                        'Registered',
                        f"New influencer registered - Platforms: {', '.join(platforms) if platforms else 'None'}"
                    ])
        
        # For 'all' type, sort by date and write
        if history_type == 'all':
            # Sort all data by date (index 1)
            all_data.sort(key=lambda x: x[1], reverse=True)
            for row in all_data:
                writer.writerow(row)
        
        # Create response
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = f'attachment; filename={filename}'
        
        return response

    @app.route('/astats')
    def admin_stats():
        user_distribution = get_user_distribution()
        campaign_count = get_campaign_count()
        top_industries = get_top_industries()
        budget_distribution = get_campaign_budget_distribution()
        monthly_registrations = get_monthly_registrations()
        application_status = get_application_status_distribution()
        campaign_duration = get_campaign_duration_analysis()
        influencer_platforms = get_influencer_engagement_stats()

        return render_template('astats.html',
                               user_distribution=json.dumps(user_distribution),
                               campaign_count=json.dumps(campaign_count),
                               top_industries=json.dumps(top_industries),
                               budget_distribution=json.dumps(budget_distribution),
                               monthly_registrations=json.dumps(monthly_registrations),
                               application_status=json.dumps(application_status),
                               campaign_duration=json.dumps(campaign_duration),
                               influencer_platforms=json.dumps(influencer_platforms))
        
    @app.route('/istats')
    def influ_stats():
        return render_template('influ_stats.html')

    @app.route('/ihistory')
    def influencer_history():
        if 'influencer_id' not in session:
            flash('You need to log in first.', 'error')
            return redirect(url_for('influ_log'))
        
        influencer = Influencer.query.get(session['influencer_id'])
        filter_type = request.args.get('filter', 'overall')
        
        # Calculate date ranges
        now = datetime.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = now - timedelta(days=7)
        month_start = now - timedelta(days=30)
        
        # Base queries for influencer's data
        applications_query = Application.query.filter_by(influencer_id=influencer.id)
        transactions_query = WalletTransaction.query.filter_by(user_id=influencer.id, user_type='influencer')
        payments_query = Payment.query.filter_by(influencer_id=influencer.id)
        
        # Apply date filters
        if filter_type == 'today':
            applications = applications_query.filter(Application.created_at >= today_start).all()
            transactions = transactions_query.filter(WalletTransaction.created_at >= today_start).all()
            payments = payments_query.filter(Payment.payment_date >= today_start).all()
            title = "Today's History"
        elif filter_type == 'week':
            applications = applications_query.filter(Application.created_at >= week_start).all()
            transactions = transactions_query.filter(WalletTransaction.created_at >= week_start).all()
            payments = payments_query.filter(Payment.payment_date >= week_start).all()
            title = "Last Week's History"
        elif filter_type == 'month':
            applications = applications_query.filter(Application.created_at >= month_start).all()
            transactions = transactions_query.filter(WalletTransaction.created_at >= month_start).all()
            payments = payments_query.filter(Payment.payment_date >= month_start).all()
            title = "Last Month's History"
        else:  # overall
            applications = applications_query.all()
            transactions = transactions_query.all()
            payments = payments_query.all()
            title = "Complete History"
        
        # Calculate summary statistics
        total_earned = sum(t.amount for t in transactions if t.transaction_type == 'credit')
        total_withdrawn = sum(t.amount for t in transactions if t.transaction_type == 'withdrawal')
        total_applications = len(applications)
        total_payments = len(payments)
        accepted_campaigns = len([app for app in applications if app.status == 'accepted'])
        
        # Debug information
        print(f"DEBUG - Influencer ID: {influencer.id}")
        print(f"DEBUG - Transactions count: {len(transactions)}")
        print(f"DEBUG - Applications count: {len(applications)}")
        print(f"DEBUG - Payments count: {len(payments)}")
        print(f"DEBUG - Credit transactions: {[t.amount for t in transactions if t.transaction_type == 'credit']}")
        print(f"DEBUG - Withdrawal transactions: {[t.amount for t in transactions if t.transaction_type == 'withdrawal']}")
        print(f"DEBUG - Total earned: {total_earned}")
        print(f"DEBUG - Total withdrawn: {total_withdrawn}")
        print(f"DEBUG - Accepted campaigns: {accepted_campaigns}")
        print(f"DEBUG - Current balance: {influencer.wallet_balance}")
        
        summary = {
            'total_earned': total_earned,
            'total_withdrawn': total_withdrawn,
            'total_applications': total_applications,
            'total_payments': total_payments,
            'accepted_campaigns': accepted_campaigns,
            'current_balance': influencer.wallet_balance
        }
        
        return render_template('influ_history.html',
                               influencer=influencer,
                               applications=applications,
                               transactions=transactions,
                               payments=payments,
                               filter_type=filter_type,
                               title=title,
                               summary=summary,
                               current_date=now.date())

    @app.route('/ihistory/download')
    def download_influencer_history():
        if 'influencer_id' not in session:
            flash('You need to log in first.', 'error')
            return redirect(url_for('influ_log'))
        
        influencer = Influencer.query.get(session['influencer_id'])
        filter_type = request.args.get('filter', 'overall')
        history_type = request.args.get('type', 'all')
        
        # Calculate date ranges
        now = datetime.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = now - timedelta(days=7)
        month_start = now - timedelta(days=30)
        
        # Base queries for influencer's data
        applications_query = Application.query.filter_by(influencer_id=influencer.id)
        transactions_query = WalletTransaction.query.filter_by(user_id=influencer.id, user_type='influencer')
        payments_query = Payment.query.filter_by(influencer_id=influencer.id)
        
        # Apply date filters
        if filter_type == 'today':
            applications = applications_query.filter(Application.created_at >= today_start).all()
            transactions = transactions_query.filter(WalletTransaction.created_at >= today_start).all()
            payments = payments_query.filter(Payment.payment_date >= today_start).all()
            period_suffix = "today"
        elif filter_type == 'week':
            applications = applications_query.filter(Application.created_at >= week_start).all()
            transactions = transactions_query.filter(WalletTransaction.created_at >= week_start).all()
            payments = payments_query.filter(Payment.payment_date >= week_start).all()
            period_suffix = "week"
        elif filter_type == 'month':
            applications = applications_query.filter(Application.created_at >= month_start).all()
            transactions = transactions_query.filter(WalletTransaction.created_at >= month_start).all()
            payments = payments_query.filter(Payment.payment_date >= month_start).all()
            period_suffix = "month"
        else:  # overall
            applications = applications_query.all()
            transactions = transactions_query.all()
            payments = payments_query.all()
            period_suffix = "overall"
        
        # Apply history type filter
        if history_type == 'applications':
            transactions = []
            payments = []
            type_suffix = "applications"
        elif history_type == 'transactions':
            applications = []
            payments = []
            type_suffix = "transactions"
        elif history_type == 'payments':
            applications = []
            transactions = []
            type_suffix = "payments"
        else:  # all
            type_suffix = "all"
        
        # Generate filename based on filters
        filename = f"influencer_history_{period_suffix}_{type_suffix}_{now.strftime('%Y%m%d')}.csv"
        
        # Create CSV content
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write appropriate headers based on history type
        if history_type == 'applications':
            writer.writerow(['Application Date', 'Campaign', 'Sponsor', 'Budget', 'Status', 'Campaign Description'])
        elif history_type == 'transactions':
            writer.writerow(['Date', 'Transaction Type', 'Amount', 'Description', 'Reference ID'])
        elif history_type == 'payments':
            writer.writerow(['Payment Date', 'Campaign', 'Sponsor', 'Amount', 'Status'])
        else:  # all types
            writer.writerow(['Type', 'Date', 'Campaign/Transaction', 'Sponsor', 'Amount', 'Status', 'Description'])
        
        # Application data
        for application in applications:
            if history_type == 'applications':
                writer.writerow([
                    application.created_at.strftime('%Y-%m-%d %H:%M'),
                    application.campaign.name,
                    application.campaign.sponsor.username,
                    f"₹{application.campaign.budget:.2f}",
                    application.status.title(),
                    application.campaign.description[:100] + '...' if len(application.campaign.description) > 100 else application.campaign.description
                ])
            else:
                writer.writerow([
                    'Application',
                    application.created_at.strftime('%Y-%m-%d %H:%M'),
                    application.campaign.name,
                    application.campaign.sponsor.username,
                    f"₹{application.campaign.budget:.2f}",
                    application.status.title(),
                    f"Applied to {application.campaign.name}"
                ])
        
        # Transaction data
        for transaction in transactions:
            if history_type == 'transactions':
                writer.writerow([
                    transaction.created_at.strftime('%Y-%m-%d %H:%M'),
                    transaction.transaction_type.title(),
                    f"₹{transaction.amount:.2f}",
                    transaction.description,
                    transaction.reference_id if transaction.reference_id else 'N/A'
                ])
            else:
                writer.writerow([
                    'Transaction',
                    transaction.created_at.strftime('%Y-%m-%d %H:%M'),
                    transaction.transaction_type.title(),
                    '-',
                    f"₹{transaction.amount:.2f}",
                    'Completed',
                    transaction.description
                ])
        
        # Payment data
        for payment in payments:
            if history_type == 'payments':
                writer.writerow([
                    payment.payment_date.strftime('%Y-%m-%d %H:%M'),
                    payment.campaign.name,
                    payment.campaign.sponsor.username,
                    f"₹{payment.amount:.2f}",
                    payment.status.title()
                ])
            else:
                writer.writerow([
                    'Payment',
                    payment.payment_date.strftime('%Y-%m-%d %H:%M'),
                    payment.campaign.name,
                    payment.campaign.sponsor.username,
                    f"₹{payment.amount:.2f}",
                    payment.status.title(),
                    f"Payment from {payment.campaign.sponsor.username} for {payment.campaign.name}"
                ])
        
        # Create response
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = f'attachment; filename={filename}'
        
        return response

    @app.route('/sstats')
    def sstats():
        total_campaigns = Campaign.query.count()
        active_campaigns = Campaign.query.filter_by(status='active').count()
        completed_campaigns = Campaign.query.filter_by(status='completed').count()
        total_budget = db.session.query(db.func.sum(Campaign.budget)).scalar()

        stats = {
            'total_campaigns': total_campaigns,
            'active_campaigns': active_campaigns,
            'completed_campaigns': completed_campaigns,
            'total_budget': total_budget
        }

        return render_template('spon_stats.html', stats=stats)

    @app.route('/shistory')
    def sponsor_history():
        if 'sponsor_id' not in session:
            flash('You need to log in first.', 'error')
            return redirect(url_for('spon_log'))
        
        sponsor = Sponsor.query.get(session['sponsor_id'])
        filter_type = request.args.get('filter', 'overall')
        
        # Calculate date ranges
        now = datetime.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = now - timedelta(days=7)
        month_start = now - timedelta(days=30)
        
        # Base queries for sponsor's data
        campaigns_query = Campaign.query.filter_by(sponsor_id=sponsor.id)
        transactions_query = WalletTransaction.query.filter_by(user_id=sponsor.id, user_type='sponsor')
        payments_query = Payment.query.filter_by(sponsor_id=sponsor.id)
        
        # Apply date filters
        if filter_type == 'today':
            campaigns = campaigns_query.filter(Campaign.created_at >= today_start).all()
            transactions = transactions_query.filter(WalletTransaction.created_at >= today_start).all()
            payments = payments_query.filter(Payment.payment_date >= today_start).all()
            title = "Today's History"
        elif filter_type == 'week':
            campaigns = campaigns_query.filter(Campaign.created_at >= week_start).all()
            transactions = transactions_query.filter(WalletTransaction.created_at >= week_start).all()
            payments = payments_query.filter(Payment.payment_date >= week_start).all()
            title = "Last Week's History"
        elif filter_type == 'month':
            campaigns = campaigns_query.filter(Campaign.created_at >= month_start).all()
            transactions = transactions_query.filter(WalletTransaction.created_at >= month_start).all()
            payments = payments_query.filter(Payment.payment_date >= month_start).all()
            title = "Last Month's History"
        else:  # overall
            campaigns = campaigns_query.all()
            transactions = transactions_query.all()
            payments = payments_query.all()
            title = "Complete History"
        
        # Get accepted applications for campaigns
        campaign_applications = {}
        for campaign in campaigns:
            accepted_apps = Application.query.filter_by(
                campaign_id=campaign.id, 
                status='accepted'
            ).all()
            campaign_applications[campaign.id] = accepted_apps
        
        # Calculate summary statistics
        total_spent = sum(t.amount for t in transactions if t.transaction_type == 'debit')
        total_recharged = sum(t.amount for t in transactions if t.transaction_type == 'recharge')
        total_campaigns = len(campaigns)
        total_payments = len(payments)
        
        summary = {
            'total_spent': total_spent,
            'total_recharged': total_recharged,
            'total_campaigns': total_campaigns,
            'total_payments': total_payments,
            'current_balance': sponsor.wallet_balance
        }
        
        return render_template('spon_history.html',
                               sponsor=sponsor,
                               campaigns=campaigns,
                               transactions=transactions,
                               payments=payments,
                               campaign_applications=campaign_applications,
                               filter_type=filter_type,
                               title=title,
                               summary=summary,
                               current_date=now.date())

    @app.route('/shistory/download')
    def download_sponsor_history():
        if 'sponsor_id' not in session:
            flash('You need to log in first.', 'error')
            return redirect(url_for('spon_log'))
        
        sponsor = Sponsor.query.get(session['sponsor_id'])
        filter_type = request.args.get('filter', 'overall')
        history_type = request.args.get('type', 'all')
        
        # Calculate date ranges (same as history route)
        now = datetime.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = now - timedelta(days=7)
        month_start = now - timedelta(days=30)
        
        # Base queries for sponsor's data
        campaigns_query = Campaign.query.filter_by(sponsor_id=sponsor.id)
        transactions_query = WalletTransaction.query.filter_by(user_id=sponsor.id, user_type='sponsor')
        payments_query = Payment.query.filter_by(sponsor_id=sponsor.id)
        
        # Apply date filters
        if filter_type == 'today':
            campaigns = campaigns_query.filter(Campaign.created_at >= today_start).all()
            transactions = transactions_query.filter(WalletTransaction.created_at >= today_start).all()
            payments = payments_query.filter(Payment.payment_date >= today_start).all()
            period_suffix = "today"
        elif filter_type == 'week':
            campaigns = campaigns_query.filter(Campaign.created_at >= week_start).all()
            transactions = transactions_query.filter(WalletTransaction.created_at >= week_start).all()
            payments = payments_query.filter(Payment.payment_date >= week_start).all()
            period_suffix = "week"
        elif filter_type == 'month':
            campaigns = campaigns_query.filter(Campaign.created_at >= month_start).all()
            transactions = transactions_query.filter(WalletTransaction.created_at >= month_start).all()
            payments = payments_query.filter(Payment.payment_date >= month_start).all()
            period_suffix = "month"
        else:  # overall
            campaigns = campaigns_query.all()
            transactions = transactions_query.all()
            payments = payments_query.all()
            period_suffix = "overall"
        
        # Apply history type filter
        if history_type == 'campaigns':
            transactions = []
            payments = []
            type_suffix = "campaigns"
        elif history_type == 'transactions':
            campaigns = []
            payments = []
            type_suffix = "transactions"
        elif history_type == 'payments':
            campaigns = []
            transactions = []
            type_suffix = "payments"
        else:  # all
            type_suffix = "all"
        
        # Generate filename based on filters
        filename = f"sponsor_history_{period_suffix}_{type_suffix}_{now.strftime('%Y%m%d')}.csv"
        
        # Create CSV content
        import csv
        import io
        from flask import make_response
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write appropriate headers based on history type
        if history_type == 'campaigns':
            writer.writerow(['Campaign Name', 'Created Date', 'Start Date', 'End Date', 'Budget', 'Influencer', 'Status', 'Description'])
        elif history_type == 'transactions':
            writer.writerow(['Date', 'Transaction Type', 'Amount', 'Description', 'Reference ID'])
        elif history_type == 'payments':
            writer.writerow(['Payment Date', 'Campaign', 'Influencer', 'Amount', 'Status'])
        else:  # all types
            writer.writerow(['Type', 'Date', 'Campaign/Transaction', 'Influencer', 'Amount', 'Status', 'Description'])
        
        # Campaign data
        for campaign in campaigns:
            accepted_apps = Application.query.filter_by(campaign_id=campaign.id, status='accepted').all()
            if history_type == 'campaigns':
                # Specific campaign format
                if accepted_apps:
                    for app in accepted_apps:
                        writer.writerow([
                            campaign.name,
                            campaign.created_at.strftime('%Y-%m-%d %H:%M'),
                            campaign.start_date.strftime('%Y-%m-%d'),
                            campaign.end_date.strftime('%Y-%m-%d'),
                            f"₹{campaign.budget:.2f}",
                            app.influencer.username,
                            'Completed',
                            campaign.description[:100] + '...' if len(campaign.description) > 100 else campaign.description
                        ])
                else:
                    writer.writerow([
                        campaign.name,
                        campaign.created_at.strftime('%Y-%m-%d %H:%M'),
                        campaign.start_date.strftime('%Y-%m-%d'),
                        campaign.end_date.strftime('%Y-%m-%d'),
                        f"₹{campaign.budget:.2f}",
                        'No influencers assigned',
                        'Active',
                        campaign.description[:100] + '...' if len(campaign.description) > 100 else campaign.description
                    ])
            else:
                # General format for 'all' type
                for app in accepted_apps:
                    writer.writerow([
                        'Campaign',
                        campaign.created_at.strftime('%Y-%m-%d %H:%M'),
                        campaign.name,
                        app.influencer.username,
                        f"₹{campaign.budget:.2f}",
                        'Completed',
                        f"Campaign with {app.influencer.username}"
                    ])
        
        # Transaction data
        for transaction in transactions:
            if history_type == 'transactions':
                # Specific transaction format
                writer.writerow([
                    transaction.created_at.strftime('%Y-%m-%d %H:%M'),
                    transaction.transaction_type.title(),
                    f"₹{transaction.amount:.2f}",
                    transaction.description,
                    transaction.reference_id if transaction.reference_id else 'N/A'
                ])
            else:
                # General format for 'all' type
                writer.writerow([
                    'Transaction',
                    transaction.created_at.strftime('%Y-%m-%d %H:%M'),
                    transaction.transaction_type.title(),
                    '-',
                    f"₹{transaction.amount:.2f}",
                    'Completed',
                    transaction.description
                ])
        
        # Payment data
        for payment in payments:
            if history_type == 'payments':
                # Specific payment format
                writer.writerow([
                    payment.payment_date.strftime('%Y-%m-%d %H:%M'),
                    payment.campaign.name,
                    payment.influencer.username,
                    f"₹{payment.amount:.2f}",
                    payment.status.title()
                ])
            else:
                # General format for 'all' type
                writer.writerow([
                    'Payment',
                    payment.payment_date.strftime('%Y-%m-%d %H:%M'),
                    payment.campaign.name,
                    payment.influencer.username,
                    f"₹{payment.amount:.2f}",
                    payment.status.title(),
                    f"Payment to {payment.influencer.username} for {payment.campaign.name}"
                ])
        
        # Create response
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = f'attachment; filename={filename}'
        
        return response

    @app.route('/sdash')
    @app.route('/sdash/<int:campaign_id>')
    @app.route('/sdash/<int:application_id>')
    def spon_dash(campaign_id=None, application_id=None):
        if 'sponsor_id' not in session:
            flash('You need to log in first.', 'error')
            return redirect(url_for('spon_log'))
        
        sponsor = Sponsor.query.get(session['sponsor_id'])
        
        # Get all campaigns by the sponsor
        all_campaigns = sponsor.campaigns
        
        # Separate campaigns into different categories
        ongoing_campaigns = []
        pending_campaigns = []
        
        for campaign in all_campaigns:
            # Check if campaign has any accepted applications
            accepted_apps = Application.query.filter_by(campaign_id=campaign.id, status='accepted').all()
            if accepted_apps:
                # Add accepted applications info to campaign
                campaign.accepted_applications = accepted_apps
                ongoing_campaigns.append(campaign)
            else:
                pending_campaigns.append(campaign)
        
        # Get pending applications for this sponsor
        applications = Application.query.filter(Application.campaign.has(sponsor_id=sponsor.id), Application.status == 'pending').all()
        
        selected_campaign = None
        selected_application = None
        
        if campaign_id:
            selected_campaign = Campaign.query.get(campaign_id)
        elif application_id:
            selected_application = Application.query.get(application_id)
        
        return render_template('spon_dash.html', 
                               sponsor=sponsor, 
                               ongoing_campaigns=ongoing_campaigns,
                               pending_campaigns=pending_campaigns, 
                               applications=applications,
                               selected_campaign=selected_campaign,
                               selected_application=selected_application)

    @app.route('/delete_campaign/<int:campaign_id>', methods=['POST'])
    def delete_campaign(campaign_id):
        if 'sponsor_id' not in session:
            flash('You need to log in first.', 'error')
            return redirect(url_for('spon_log'))

        campaign = Campaign.query.get_or_404(campaign_id)
        if campaign.sponsor_id != session['sponsor_id']:
            flash('You do not have permission to delete this campaign.', 'error')
            return redirect(url_for('spon_dash'))

        try:
            campaign_name = campaign.name
            
            # First, delete all applications related to this campaign
            applications = Application.query.filter_by(campaign_id=campaign_id).all()
            for application in applications:
                db.session.delete(application)
            
            # Flush the session to ensure applications are deleted before deleting campaign
            db.session.flush()
            
            # Now delete the campaign
            db.session.delete(campaign)
            db.session.commit()
            
            flash(f'Campaign "{campaign_name}" and all related data deleted successfully.', 'success')
            
        except Exception as e:
            db.session.rollback()
            flash('There was an error deleting the campaign. Please try again.', 'error')
            print(f"Error deleting campaign: {e}")  # For debugging

        return redirect(url_for('spon_dash'))

    @app.route('/swallet', methods=['GET', 'POST'])
    def sponsor_wallet():
        if 'sponsor_id' not in session:
            flash('You need to log in first.', 'error')
            return redirect(url_for('spon_log'))
        
        sponsor = Sponsor.query.get(session['sponsor_id'])
        
        if request.method == 'POST':
            recharge_amount = float(request.form.get('amount', 0))
            payment_method = request.form.get('payment_method')
            
            if recharge_amount > 0:
                # Simulate successful payment processing
                sponsor.wallet_balance += recharge_amount
                
                # Create transaction record
                transaction = WalletTransaction(
                    user_id=sponsor.id,
                    user_type='sponsor',
                    transaction_type='recharge',
                    amount=recharge_amount,
                    description=f'Wallet recharge via {payment_method}',
                    reference_id=str(uuid.uuid4())[:8]
                )
                
                db.session.add(transaction)
                db.session.commit()
                
                flash(f'Successfully recharged ₹{recharge_amount:.2f} to your wallet!', 'success')
            else:
                flash('Please enter a valid amount.', 'error')
                
            return redirect(url_for('sponsor_wallet'))
        
        # Get transaction history
        transactions = WalletTransaction.query.filter_by(
            user_id=sponsor.id, 
            user_type='sponsor'
        ).order_by(WalletTransaction.created_at.desc()).limit(20).all()
        
        return render_template('swallet.html', 
                               sponsor=sponsor, 
                               transactions=transactions)

    @app.route('/iwallet', methods=['GET', 'POST'])
    def influencer_wallet():
        if 'influencer_id' not in session:
            flash('You need to log in first.', 'error')
            return redirect(url_for('influ_log'))
        
        influencer = Influencer.query.get(session['influencer_id'])
        
        if request.method == 'POST':
            action = request.form.get('action')
            
            if action == 'update_bank':
                influencer.bank_account = request.form.get('bank_account')
                influencer.ifsc_code = request.form.get('ifsc_code')
                db.session.commit()
                flash('Bank details updated successfully!', 'success')
                
            elif action == 'withdraw':
                withdrawal_amount = float(request.form.get('amount', 0))
                
                if withdrawal_amount > 0 and withdrawal_amount <= influencer.wallet_balance:
                    influencer.wallet_balance -= withdrawal_amount
                    
                    # Create transaction record
                    transaction = WalletTransaction(
                        user_id=influencer.id,
                        user_type='influencer',
                        transaction_type='withdrawal',
                        amount=withdrawal_amount,
                        description=f'Withdrawal to bank account {influencer.bank_account}',
                        reference_id=str(uuid.uuid4())[:8]
                    )
                    
                    db.session.add(transaction)
                    db.session.commit()
                    
                    flash(f'Successfully withdrawn ₹{withdrawal_amount:.2f} to your bank account!', 'success')
                else:
                    flash('Invalid withdrawal amount or insufficient balance.', 'error')
                    
            return redirect(url_for('influencer_wallet'))
        
        # Get transaction history
        transactions = WalletTransaction.query.filter_by(
            user_id=influencer.id, 
            user_type='influencer'
        ).order_by(WalletTransaction.created_at.desc()).limit(20).all()
        
        return render_template('iwallet.html', 
                               influencer=influencer, 
                               transactions=transactions)

    @app.route('/accept_application/<int:application_id>', methods=['POST'])
    def accept_application(application_id):
        if 'sponsor_id' not in session:
            flash('You need to log in first.', 'error')
            return redirect(url_for('spon_log'))

        application = Application.query.get_or_404(application_id)
        
        if application.campaign.sponsor_id != session['sponsor_id']:
            flash('You do not have permission to accept this application.', 'error')
            return redirect(url_for('spon_dash'))

        if application.status != 'pending':
            flash('This application has already been processed.', 'warning')
            return redirect(url_for('spon_dash'))

        sponsor = Sponsor.query.get(session['sponsor_id'])
        campaign_budget = application.campaign.budget
        
        # Check if sponsor has sufficient balance
        if sponsor.wallet_balance < campaign_budget:
            flash(f'Insufficient wallet balance. You need ₹{campaign_budget:.2f} to accept this application. Please recharge your wallet.', 'error')
            return redirect(url_for('spon_dash'))

        try:
            # Process automatic payment
            sponsor.wallet_balance -= campaign_budget
            application.influencer.wallet_balance += campaign_budget
            
            application.status = 'accepted'
            
            # Check if influencer is already in campaign influencers list to avoid duplicates
            if application.influencer not in application.campaign.influencers:
                application.campaign.influencers.append(application.influencer)
            
            # Create payment record
            payment = Payment(
                sponsor_id=sponsor.id,
                influencer_id=application.influencer.id,
                campaign_id=application.campaign.id,
                amount=campaign_budget,
                status='completed'
            )
            db.session.add(payment)
            
            # Create transaction records
            sponsor_transaction = WalletTransaction(
                user_id=sponsor.id,
                user_type='sponsor',
                transaction_type='debit',
                amount=campaign_budget,
                description=f'Payment to {application.influencer.username} for campaign {application.campaign.name}',
                reference_id=f'campaign_{application.campaign.id}'
            )
            
            influencer_transaction = WalletTransaction(
                user_id=application.influencer.id,
                user_type='influencer',
                transaction_type='credit',
                amount=campaign_budget,
                description=f'Payment received from {sponsor.username} for campaign {application.campaign.name}',
                reference_id=f'campaign_{application.campaign.id}'
            )
            
            db.session.add(sponsor_transaction)
            db.session.add(influencer_transaction)
            db.session.commit()

            flash(f"Application accepted! ₹{campaign_budget:.2f} has been paid to {application.influencer.username}.", 'success')
            
        except Exception as e:
            db.session.rollback()
            flash('Error processing payment. Please try again.', 'error')
            print(f"Payment error: {e}")
            
        return redirect(url_for('spon_dash'))

    @app.route('/reject_application/<int:application_id>', methods=['POST'])
    def reject_application(application_id):
        if 'sponsor_id' not in session:
            flash('You need to log in first.', 'error')
            return redirect(url_for('spon_log'))

        application = Application.query.get_or_404(application_id)
        
        if application.campaign.sponsor_id != session['sponsor_id']:
            flash('You do not have permission to reject this application.', 'error')
            return redirect(url_for('spon_dash'))

        if application.status != 'pending':
            flash('This application has already been processed.', 'warning')
            return redirect(url_for('spon_dash'))

        application.status = 'rejected'
        db.session.commit()

        flash(f"Application from {application.influencer.username} for {application.campaign.name} has been rejected.", 'info')
        return redirect(url_for('spon_dash'))

    @app.route('/spon_camp', methods=['GET', 'POST'])
    def spon_camp():
        if 'sponsor_id' not in session:
            flash('You need to log in first.', 'error')
            return redirect(url_for('spon_log'))

        if request.method == 'POST':
            sponsor_id = session['sponsor_id']
            name = request.form['name']
            description = request.form['description']
            start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()
            end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d').date()
            budget = float(request.form['budget'])

            new_campaign = Campaign(
                name=name,
                description=description,
                start_date=start_date,
                end_date=end_date,
                budget=budget,
                sponsor_id=sponsor_id
            )
            db.session.add(new_campaign)
            db.session.commit()
            flash('Campaign created successfully!', 'success')
            return redirect(url_for('spon_dash'))

        return render_template('spon_camp.html')

    @app.route('/apply_campaign/<int:campaign_id>', methods=['POST'])
    def apply_campaign(campaign_id):
        if 'influencer_id' not in session:
            flash('You need to log in as an influencer first.', 'error')
            return redirect(url_for('influ_log'))

        campaign = Campaign.query.get_or_404(campaign_id)
        influencer = Influencer.query.get(session['influencer_id'])

        existing_application = Application.query.filter_by(
            influencer_id=influencer.id, 
            campaign_id=campaign.id
        ).first()

        if existing_application:
            flash('You have already applied to this campaign.', 'warning')
        else:
            new_application = Application(
                influencer_id=influencer.id,
                campaign_id=campaign.id,
                status='pending'
            )
            db.session.add(new_application)
            db.session.commit()
            
            # Set session flag for success modal
            session['application_success'] = {
                'campaign_name': campaign.name,
                'sponsor_name': campaign.sponsor.username
            }

        # Redirect to the page the user came from
        return_url = request.form.get('return_url', url_for('ifind'))
        return redirect(return_url)

    @app.route('/influencer/<username>')
    def influencer_profile(username):
        influencer = Influencer.query.filter_by(username=username).first_or_404()
        return render_template('influ_profile.html', influencer=influencer)

    @app.route('/sfind')
    def sfind():
        search_query = request.args.get('search', '')
        searched_influencer = None

        if search_query:
            searched_influencer = Influencer.query.filter_by(username=search_query).first()

        influencers = Influencer.query.all()
        campaigns = Campaign.query.filter(Campaign.end_date >= datetime.now().date()).all()
        
        return render_template('spon_find.html', 
                               influencers=influencers, 
                               campaigns=campaigns, 
                               search_query=search_query,
                               searched_influencer=searched_influencer)

    @app.route('/ifind', methods=['GET', 'POST'])
    def ifind():
        if 'influencer_id' not in session:
            flash('You need to log in first.', 'error')
            return redirect(url_for('influ_log'))
            
        influencer = Influencer.query.get(session['influencer_id'])
        search_query = request.form.get('search_query', '') if request.method == 'POST' else request.args.get('search', '')
        searched_sponsor = None
        searched_campaigns = None

        if search_query:
            searched_sponsor = Sponsor.query.filter(Sponsor.username.contains(search_query)).all()
            searched_campaigns = Campaign.query.filter(
                (Campaign.name.contains(search_query)) | 
                (Campaign.sponsor.has(Sponsor.username.contains(search_query))),
                Campaign.end_date >= datetime.now().date()
            ).all()

        sponsors = Sponsor.query.all()
        
        # Get campaigns that influencer hasn't applied to
        applied_campaign_ids = [app.campaign_id for app in influencer.applications]
        campaigns = Campaign.query.filter(
            ~Campaign.id.in_(applied_campaign_ids),
            Campaign.end_date >= datetime.now().date()
        ).all()

        return render_template('influ_find.html', 
                               sponsors=sponsors, 
                               campaigns=campaigns, 
                               search_query=search_query,
                               searched_sponsor=searched_sponsor,
                               searched_campaigns=searched_campaigns,
                               influencer=influencer)
