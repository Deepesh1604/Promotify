from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime , timedelta
import sqlalchemy
from sqlalchemy import func
from sqlalchemy import or_
import json

app = Flask(__name__)#creta new flask instance
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # it set to false to improve performance since event isn't used in the application 
app.config['SECRET_KEY'] = 'your_secret_key'  
db = SQLAlchemy(app)#creates a SQLAlchemy object and binds it to your Flask application

ADMIN_EMAIL = 'admin@gmail.com'
ADMIN_PASSWORD = 'admin123'

class Influencer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True, nullable=False)
    email = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(10), nullable=False)
    instagram = db.Column(db.String(15), unique=True, nullable=True)
    linkedin = db.Column(db.String(20), unique=True, nullable=True)
    twitter = db.Column(db.String(20), unique=True, nullable=True)
    youtube = db.Column(db.String(20), unique=True, nullable=True)
    date_joined = db.Column(db.DateTime, default=datetime.utcnow)  # Add this line
    campaigns = db.relationship('Campaign', secondary='application', 
                                primaryjoin="and_(Influencer.id==Application.influencer_id, Application.status=='accepted')",
                                backref=db.backref('accepted_influencers', lazy='dynamic'))

class Sponsor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True, nullable=False)
    email = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(10), nullable=False)
    industry = db.Column(db.String(20), nullable=False)
    date_joined = db.Column(db.DateTime, default=datetime.utcnow)  # Add this line

class Campaign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sponsor_id = db.Column(db.Integer, db.ForeignKey('sponsor.id'), nullable=False)
    name = db.Column(db.String(15), nullable=False)
    description = db.Column(db.Text, nullable=True)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    budget = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50))
    sponsor = db.relationship('Sponsor', backref=db.backref('campaigns', lazy=True))
    influencers = db.relationship('Influencer', secondary='application', 
                                  primaryjoin="and_(Campaign.id==Application.campaign_id, Application.status=='accepted')",
                                  backref=db.backref('accepted_campaigns', lazy='dynamic'))

    def __repr__(self):
        return f"Campaign('{self.name}')"

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    influencer_id = db.Column(db.Integer, db.ForeignKey('influencer.id'), nullable=False)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)
    status = db.Column(db.String(20), default='pending') 
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    influencer = db.relationship('Influencer', backref=db.backref('applications', lazy=True))
    campaign = db.relationship('Campaign', backref=db.backref('applications', lazy=True))

    def __repr__(self):
        return f"<Application {self.id}: {self.influencer.username} for {self.campaign.name}>"


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
    available_campaigns = Campaign.query.filter(~Campaign.influencers.contains(influencer)).all()
    
    selected_campaign = None
    if campaign_id:
        selected_campaign = Campaign.query.get(campaign_id)
    
    return render_template('influ_dash.html', 
                           influencer=influencer, 
                           active_campaigns=available_campaigns,
                           selected_campaign=selected_campaign)


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

# @app.route('/view_campaign/<int:campaign_id>')
# def view_campaign(campaign_id):
#     if 'admin_logged_in' not in session or not session['admin_logged_in']:
#         flash('You need to log in first.', 'error')
#         return redirect(url_for('admin_log'))

#     campaign = Campaign.query.get_or_404(campaign_id)
#     return render_template('view_campaign.html', campaign=campaign)

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

    campaign = Campaign.query.get_or_404(campaign_id)
    db.session.delete(campaign)
    db.session.commit()
    flash(f'Campaign "{campaign.name}" has been removed.', 'success')
    
    search_query = request.args.get('search', '')
    filter_options = request.args.getlist('filter')
    return redirect(url_for('afind', search=search_query, filter=filter_options))

    influencer = Influencer.query.get_or_404(influencer_id)
    db.session.delete(influencer)
    db.session.commit()
    flash(f'Influencer "{influencer.username}" has been removed.', 'success')
    return redirect(url_for('a_find'))

from sqlalchemy import func, extract

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

# ... (your existing imports and app setup)

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

@app.route('/astats')
def admin_stats():
    user_distribution = get_user_distribution()
    campaign_count = get_campaign_count()
    top_industries = get_top_industries()

    return render_template('astats.html',
                           user_distribution=json.dumps(user_distribution),
                           campaign_count=json.dumps(campaign_count),
                           top_industries=json.dumps(top_industries))
    
@app.route('/istats')
def influ_stats():
    return render_template('influ_stats.html')

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

@app.route('/sdash')
@app.route('/sdash/<int:campaign_id>')
@app.route('/sdash/<int:application_id>')
def spon_dash(campaign_id=None, application_id=None):
    if 'sponsor_id' not in session:
        flash('You need to log in first.', 'error')
        return redirect(url_for('spon_log'))
    
    sponsor = Sponsor.query.get(session['sponsor_id'])
    campaigns = sponsor.campaigns
    applications = Application.query.filter(Application.campaign.has(sponsor_id=sponsor.id), Application.status == 'pending').all()
    
    selected_campaign = None
    selected_application = None
    
    if campaign_id:
        selected_campaign = Campaign.query.get(campaign_id)
    elif application_id:
        selected_application = Application.query.get(application_id)
    
    return render_template('spon_dash.html', 
                           sponsor=sponsor, 
                           campaigns=campaigns, 
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
        # Fetch applications related to the campaign
        applications = Application.query.filter_by(campaign_id=campaign_id).all()
        for application in applications:
            db.session.delete(application)

        db.session.delete(campaign)
        db.session.commit()
        flash('Campaign and related applications deleted successfully.', 'success')
    except sqlalchemy.orm.exc.StaleDataError:
        db.session.rollback()
        flash('There was an error deleting the campaign. Please try again.', 'error')

    return redirect(url_for('spon_dash'))

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

    application.status = 'accepted'
    application.campaign.influencers.append(application.influencer)
    db.session.commit()

    flash(f"Application from {application.influencer.username} for {application.campaign.name} has been accepted.", 'success')
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
        flash('Your application has been submitted successfully!', 'success')

    return redirect(url_for('ifind'))

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

@app.route('/ifind')
def ifind():
    search_query = request.args.get('search', '')
    searched_sponsor = None
    searched_campaigns = None

    if search_query:
        searched_sponsor = Sponsor.query.filter_by(username=search_query).all()
        searched_campaigns = Campaign.query.filter(
            (Campaign.name.contains(search_query)) | 
            (Campaign.sponsor.has(Sponsor.username.contains(search_query)))
        ).all()

    sponsors = Sponsor.query.all()
    campaigns = Campaign.query.filter(Campaign.end_date >= datetime.now().date()).all()

    return render_template('influ_find.html', 
                           sponsors=sponsors, 
                           campaigns=campaigns, 
                           search_query=search_query,
                           searched_sponsor=searched_sponsor,
                           searched_campaigns=searched_campaigns)


if __name__ == "__main__":
    app.run(debug=True , port = 5000)
