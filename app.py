import os
import bcrypt
from flask import Flask, render_template, request, redirect, url_for, session
from flask_pymongo import PyMongo
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



####             ####
#                   #
#       INDEX       #
#                   #
####             #### 
@app.route('/')
def index():
    username = None
    
    if 'user_id' in session:
        user_id = session['user_id']
        user = mongo.db.users.find_one({'_id': ObjectId(user_id)})

        if user:
            username = user['username']

    return render_template('index.html', username=username)

####               ####
#                     #
#       PROFILE       #
#                     #
####               #### 
@app.route('/profile')
def profile():
 return render_template('profile.html')

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

        # ADD MORE CHECKS HERE 
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
        
        # User exists already?
        email = mongo.db.users.find_one({'email': email})
        if email and bcrypt.checkpw(password.encode('utf-8'), email['password']):
            session['user_id'] = str(email['_id'])
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
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))



if __name__ == '__main__':
    app.run(debug=True)