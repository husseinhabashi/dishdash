from flask import Flask
from flask_pymongo import PyMongo
from flask_login import LoginManager
from .config import Config
from .routes import register_routes
from .models.user import User

# -------------------------
# App Initialization
# -------------------------

app = Flask(__name__)
app.config.from_object(Config)

# Validate environment variables
Config.validate()

# -------------------------
# MongoDB Setup
# -------------------------

mongo = PyMongo(app)
app.db = mongo.db
app.users_collection = mongo.db.users

# -------------------------
# Login Manager Setup
# -------------------------

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
app.login_manager = login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.get(app.users_collection, user_id)

# -------------------------
# Register Routes
# -------------------------

register_routes(app)

# -------------------------
# Run the App
# -------------------------

if __name__ == '__main__':
    app.run(debug=True)