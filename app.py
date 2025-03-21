import os
import logging
from datetime import datetime
from bson.objectid import ObjectId

import bcrypt
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_pymongo import PyMongo
from werkzeug.utils import secure_filename

# Load environment variables
load_dotenv()

# Initialize Flask app and configurations
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["MONGO_URI"] = os.getenv("MONGO_URI")
app.config['UPLOAD_FOLDER'] = 'static/img/uploads/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Configure logging
logging.basicConfig(level=logging.INFO)

# Check required env variables
if not app.config["MONGO_URI"]:
    logging.error("MONGO_URI is not set. Please check your .env file.")
else:
    logging.info("MONGO_URI loaded successfully.")

if not app.config["SECRET_KEY"]:
    logging.error("SECRET_KEY is not set. Please check your .env file.")
else:
    logging.info("SECRET_KEY loaded successfully.")

# Initialize MongoDB
mongo = PyMongo(app)
db = mongo.db
users_collection = db.users

try:
    count = users_collection.count_documents({})
    if count is not None:
        logging.info("Successfully connected to the database.")
    else:
        logging.error("Failed to access the database.")
except Exception as e:
    logging.error(f"Error accessing the 'users' collection: {e}")

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


class User(UserMixin):
    """User class for Flask-Login."""
    def __init__(self, user_id, username):
        self.id = user_id
        self.username = username

    @staticmethod
    def get(user_id):
        """Fetch user from MongoDB by user_id."""
        try:
            user_data = users_collection.find_one({"_id": ObjectId(user_id)})
            if user_data:
                return User(str(user_data['_id']), user_data['username'])
        except Exception as e:
            logging.error(f"Error fetching user: {e}")
        return None


@login_manager.user_loader
def load_user(user_id):
    """ returns User object or None """
    return User.get(user_id)


def allowed_file(filename):
    """ Make sure the file has a valid extension """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_current_user_document():
    """ Get document for the logged in user through flask-login current_user or session (fallback) """
    if current_user.is_authenticated:
        try:
            return users_collection.find_one({"_id": ObjectId(current_user.id)})
        except Exception as e:
            logging.error(f"Invalid user_id format: {e}")
    elif 'user_id' in session:
        try:
            return users_collection.find_one({"_id": ObjectId(session['user_id'])})
        except Exception as e:
            logging.error(f"Invalid session user_id format: {e}")
    return None


# -----------------------------
#            ROUTES
# -----------------------------

@app.route('/')
def index():
    """ If logged in, then get username and profile picture. Show defaults if not logged in. """
    user = get_current_user_document()
    username = user['username'] if user else None
    profile_pic = user.get('profile_picture', 'default_picture.jpg') if user else 'default_picture.jpg'

    return render_template('index.html', username=username, profile_pic=f'img/uploads/{profile_pic}')


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """ display profile data, update user data (profile image, username, password, etc.) """
    user = get_current_user_document()
    if not user:
        logging.error("User not found in MongoDB!")
        return redirect(url_for('login'))
        
    profile_pic = user.get('profile_picture', 'default_picture.jpg')

    if request.method == 'POST':
        action = request.form.get("action")
        # Process file upload for profile picture
        if action == "upload_image":
            file = request.files.get('profile-pic')
            if not file or file.filename == '':
                logging.info("No file selected!")
                return redirect(url_for('profile'))

            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_ext = filename.rsplit('.', 1)[1].lower()
                new_filename = f"{user['username']}.{file_ext}"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
                file.save(file_path)

                # Update MongoDB
                result = users_collection.update_one({'_id': user['_id']}, {"$set": {'profile_picture': new_filename}})
                logging.info(f"MongoDB Update Result - Modified Count: {result.modified_count}")

                if result.modified_count > 0:
                    logging.info("Profile picture updated successfully!")
                else:
                    logging.error("Failed to update profile picture in MongoDB.")

                return redirect(url_for('profile'))

            else:
                logging.error("Invalid file format! Only PNG, JPG, and JPEG are allowed.")
                return redirect(url_for('profile'))

        elif action == "save_profile":
            # No file uploaded, so assume its a username updating form
            new_username = request.form.get('username', '').strip()
            if not new_username:
                return redirect(url_for('profile'))
            
            # Check that the new username is not already taken
            if users_collection.find_one({'username': new_username, '_id': {'$ne': user['_id']}}):
                logging.info("Username already in use!")
                return redirect(url_for('profile'))

            result = users_collection.update_one({'_id': user['_id']}, {"$set": {'username': new_username}})
            logging.info(f"MongoDB Update Result - Modified Count: {result.modified_count}")

            return redirect(url_for('profile'))
            
    return render_template('profile.html', username=user['username'], profile_pic=f'img/uploads/{profile_pic}')


@app.route('/recipes')
def recipes():
    return render_template('recipes.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """ User registration - validate form inputs, check for existing usernames, hashing passwords, etc. """
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        email = request.form.get('email')

        # Validate email format (validate email, invalid characters, password strength, etc.)

        # Check if user already exists
        if users_collection.find_one({'username': username}):
            logging.info("User already exists!")
            return redirect(url_for('register'))
        
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        users_collection.insert_one({
            'username': username,
            'email': email,
            'password': hashed_password,
            'date_created': datetime.now()
        })

        logging.info("Registration successful!")
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """ Authenticate users through email and password, flask-login manages the user session """
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password')

        if not email or not password:
            logging.error("Missing email or password fields.")
            return redirect(url_for('login'))
        
        user = users_collection.find_one({'email': email})
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
            session['user_id'] = str(user['_id'])
            login_user(User(str(user['_id']), user['username']))
            logging.info("Login successful!")
            return redirect(url_for('index'))
        else:
            logging.error("Invalid email or password.")
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    """ Remove session data and logout user """
    session.pop('user_id', None) 
    logout_user()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
