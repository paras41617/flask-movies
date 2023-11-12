import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv  # Import the load_dotenv function

# Load environment variables from the .env file
load_dotenv()

# Create a Flask application instance
app = Flask(__name__)

# Configure the application with a secret key for security
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')  # Change this to a secure random key

# Configure the application with the URI for the MySQL database
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')  # Replace with your MySQL connection string

# Disable Flask-SQLAlchemy modification tracking feature
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize Flask-SQLAlchemy to work with the Flask application
db = SQLAlchemy(app)

# Initialize Flask-Login to manage user authentication
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Define a user loader function to retrieve a user by their user_id
@login_manager.user_loader
def user_loader(user_id):
    """Given *user_id*, return the associated User object.

    :param unicode user_id: user_id (email) user to retrieve
    """
    return models.User.query.get(user_id)

# Import views and models from the 'app' package
from app import views, models