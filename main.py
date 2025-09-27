from flask import Flask
from models import db
from routes import register_routes

app = Flask(__name__)  # Create new flask instance
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Set to false to improve performance since event isn't used in the application 
app.config['SECRET_KEY'] = 'your_secret_key'

# Initialize the database with the app
db.init_app(app)

# Register all routes
register_routes(app)

# Create database tables within application context
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True, port=5006)
