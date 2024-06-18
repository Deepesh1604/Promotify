from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy

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

class Sponsor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    industry = db.Column(db.String(150), nullable=False)

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
        
        if email == 'admin@gmail.com' and password == 'admin7270':  # Replace with your admin password
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

@app.route('/idash')
def influ_dash():
    return render_template('influ_dash.html')

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
def spon_dash():
    if 'sponsor_logged_in' in session and session['sponsor_logged_in']:
        return render_template('spon_dash.html')
    else:
        flash('You need to log in first.', 'error')
        return redirect(url_for('spon_log'))

@app.route('/scamp')
def spon_camp():
    if 'sponsor_logged_in' in session and session['sponsor_logged_in']:
        return render_template('spon_camp.html')
    else:
        flash('You need to log in first.', 'error')
        return redirect(url_for('spon_log'))

if __name__ == "__main__":
    app.run(debug=True)