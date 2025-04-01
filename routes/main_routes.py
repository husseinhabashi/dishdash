from flask import Blueprint, render_template, current_app
from dishdash.utils.helpers import get_current_user_document

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    user = get_current_user_document(current_app.users_collection)
    username = user['username'] if user else None
    profile_pic = user.get('profile_picture', 'default_picture.jpg') if user else 'default_picture.jpg'
    return render_template('index.html', username=username, profile_pic=f'img/uploads/{profile_pic}')

@main_bp.route('/recipes')
def recipes():
    return render_template('recipes.html')

@main_bp.route('/favorites')
def favorites():
    return render_template('favorites.html')