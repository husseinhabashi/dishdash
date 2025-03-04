import os
import bcrypt
from flask import Flask, render_template, request, redirect, url_for, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_pymongo import PyMongo
from werkzeug.utils import secure_filename
from datetime import datetime
from bson.objectid import ObjectId
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# Set env variables
MONGO_URI = os.getenv("MONGO_URI")
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

if not MONGO_URI:
    print("Error: MONGO_URI is not set. Please check your .env file.")
else:
    print("MONGO_URI loaded successfully.")

if not app.config["SECRET_KEY"]:
    print("Error: SECRET_KEY is not set. Please check your .env file.")
else:
    print("SECRET_KEY loaded successfully.")

# Access the database
app.config["MONGO_URI"] = MONGO_URI
mongo = PyMongo(app)
db = mongo.db 
users_collection = db.users 

try:
    count = users_collection.count_documents({})
    if count is not None:
        print("Successfully connected to the database.")
    else:
        print("Failed to access the database.")
except Exception as e:
    print(f"Error accessing the 'users' collection: {e}")

# Init login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

class User(UserMixin):
    def __init__(self, user_id, username):
        self.id = user_id
        self.username = username

    @staticmethod
    def get(user_id):
        """Fetch user from MongoDB by user_id."""
        user_data = mongo.db.users.find_one({"_id": ObjectId(user_id)})
        if user_data:
            return User(str(user_data['_id']), user_data['username'])
        return None

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)  # returns User object or None

####             ####
#                   #
#       INDEX       #
#                   #
####             #### 
@app.route('/')
def index():
    username = None
    profile_pic = 'default_picture.jpg'  # Default profile picture

    if 'user_id' in session:
        user_id = session['user_id']
        try:
            # Ensure user_id is properly converted to ObjectId
            user_id = ObjectId(user_id)
        except Exception as e:
            print(f"DEBUG: Invalid user_id format: {e}")
            return redirect(url_for('login'))

        user = mongo.db.users.find_one({'_id': user_id})

        if user:
            username = user['username']
            profile_pic = user.get('profile_picture', 'default_picture.jpg')  # Get profile picture if it exists
        else:
            print("DEBUG: User not found in MongoDB!")
            return redirect(url_for('login'))

    return render_template('index.html', username=username, profile_pic=f'img/uploads/{profile_pic}')




####               ####
#                     #
#       PROFILE       #
#                     #
####               #### 
UPLOAD_FOLDER = 'static/img/uploads/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    """Check if the file has a valid extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    username = None
    user_id = None
    user = None
    if 'user_id' in session:
        user_id = session['user_id']
        try:
            # Ensure user_id is properly converted to ObjectId
            user_id = ObjectId(user_id)
        except Exception as e:
            print(f"DEBUG: Invalid user_id format: {e}")
            return redirect(url_for('login'))

        user = mongo.db.users.find_one({'_id': user_id})

        if user:
            username = user['username']
        else:
            print("DEBUG: User not found in MongoDB!")
            return redirect(url_for('login'))
        
    profile_pic = user.get('profile_picture', 'default_picture.jpg')

    if request.method == 'POST':
        if 'profile-pic' in request.files:


            file = request.files['profile-pic']
            if file.filename == '':
                print("No file selected!")
                return redirect(request.url)

            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_ext = filename.rsplit('.', 1)[1].lower()
                new_filename = f"{user['username']}.{file_ext}"  # username.extension
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
            
                file.save(file_path)  # Save to uploads folder

                # Update MongoDB
                result = mongo.db.users.update_one({'_id': user_id}, {"$set": {'profile_picture': new_filename}})
                print(f"DEBUG: MongoDB Update Result - Modified Count: {result.modified_count}")

                if result.modified_count > 0:
                    print("Profile picture updated successfully!")
                else:
                    print("DEBUG: Failed to update profile picture to MongoDB")

                return redirect(url_for('profile'))  # Refresh page to reflect changes

            else:
                print("Invalid file format! Only PNG, JPG, and JPEG are allowed.")
        else:
            # no file, so assume its a username updating form
            username = request.form['username'].strip()
            if len(username) == 0: #empty username
                return redirect(url_for('profile'))
            
            existing_user = users_collection.find_one({'username': username}) #dont want to let you use someone elses username
            if existing_user:
                return redirect(url_for('profile'))

            result = users_collection.update_one({'_id': user_id}, {"$set": {'username': username}})
            print(f"DEBUG: MongoDB Update Result - Modified Count: {result.modified_count}")

            return redirect(url_for('profile'))  # Refresh page to reflect changes

    return render_template('profile.html', username=username, profile_pic=f'img/uploads/{profile_pic}')




####               ####
#                     #
#       RECIPES       #
#                     #
####               #### 
@app.route('/recipes')
def recipes():
 return render_template('recipes.html')



####                ####
#                      #
#       REGISTER       #
#                      #
####                #### 
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        email = request.form['email']

        # Validate email format (basic check for @, invalid characters, email format, password strength, etc.)
        # User exists already? 
        existing_user = users_collection.find_one({'username': username})
        if existing_user:
            print("User already exists!") # change this
            return redirect(url_for('register'))
        
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        users_collection.insert_one({
            '_id': ObjectId(),
            'username': username,
            'email': email,
            'password': hashed_password,
            'date_created': datetime.now()
        })
        
        print("Registration successful!") # change this
        return redirect(url_for('login'))

    return render_template('register.html')



####              ####
#                    #
#       LOG IN       #
#                    #
####              #### 
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if 'email' not in request.form or 'password' not in request.form:
            print("Missing fields") # change this
            return redirect(url_for('login'))
        
        email = request.form['email'].strip()
        password = request.form['password']
        
        # User exists check
        user = mongo.db.users.find_one({'email': email})
        if email and bcrypt.checkpw(password.encode('utf-8'), user['password']):
            session['user_id'] = str(user['_id'])  # Set user ID in the session
            login_user(User(str(user['_id']), user['username']))  # Log in Flask-Login
            print("Login successful!") # change this
            return redirect(url_for('index'))
        else:
            print("Invalid email or password") # change this
            return redirect(url_for('login'))

    return render_template('login.html')



####              ####
#                    #
#       LOGOUT       #
#                    #
####              #### 
@app.route('/logout')
@login_required
def logout():
    session.pop('user_id', None)  # Remove user_id from session
    logout_user()  # Log out of Flask-Login
    return redirect(url_for('index')) 



if __name__ == '__main__':
    app.run(debug=True)
