from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import sqlalchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'  # Replace with your own secret key
db = SQLAlchemy(app)


class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

class Influencer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    instagram = db.Column(db.String(150), unique=True, nullable=True)
    linkedin = db.Column(db.String(150), unique=True, nullable=True)
    twitter = db.Column(db.String(150), unique=True, nullable=True)
    youtube = db.Column(db.String(150), unique=True, nullable=True)
    campaigns = db.relationship('Campaign', secondary='application', 
                                primaryjoin="and_(Influencer.id==Application.influencer_id, Application.status=='accepted')",
                                backref=db.backref('accepted_influencers', lazy='dynamic'))

class Sponsor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    industry = db.Column(db.String(150), nullable=False)

class Campaign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sponsor_id = db.Column(db.Integer, db.ForeignKey('sponsor.id'), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    budget = db.Column(db.Float, nullable=False)
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
    status = db.Column(db.String(20), default='pending')  # 'pending', 'accepted', or 'rejected'
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
    if 'admin_logged_in' in session and session['admin_logged_in']:
        return render_template('admin_dash.html')
    else:
        flash('You need to log in first.', 'error')
        return redirect(url_for('admin_log'))

@app.route('/alogin', methods=['GET', 'POST'])
def admin_log():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        if email == 'admin@gmail.com' and password == 'admin123':
            session['admin_logged_in'] = True
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
def a_find():
    if 'admin_logged_in' in session and session['admin_logged_in']:
        return render_template('afind.html')
    else:
        flash('You need to log in first.', 'error')
        return redirect(url_for('admin_log'))

@app.route('/astats')
def a_stats():
    if 'admin_logged_in' in session and session['admin_logged_in']:
        return render_template('astats.html')
    else:
        flash('You need to log in first.', 'error')
        return redirect(url_for('admin_log'))

@app.route('/ifind')
def influ_find():
    return render_template('influ_find.html')

@app.route('/istats')
def influ_stats():
    return render_template('influ_stats.html')

@app.route('/sstats')
def spon_stats():
    if 'sponsor_logged_in' in session and session['sponsor_logged_in']:
        return render_template('spon_stats.html')
    else:
        flash('You need to log in first.', 'error')
        return redirect(url_for('spon_log'))

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

@app.route('/sfind')
def sfind():
    influencer = Influencer.query.all()
    campaigns = Campaign.query.filter(Campaign.end_date >= datetime.now().date()).all()
    
    return render_template('spon_find.html', inflencers=influencer, campaigns=campaigns)

@app.route('/ifind')
def ifind():
    sponsors = Sponsor.query.all()
    influencer = Influencer.query.all()
    campaigns = Campaign.query.filter(Campaign.end_date >= datetime.now().date()).all()
    
    return render_template('influ_find.html', sponsors=sponsors, campaigns=campaigns, influencer=influencer)


if __name__ == "__main__":
    app.run(debug=True)