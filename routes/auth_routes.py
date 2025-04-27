from flask import Blueprint, render_template, request, redirect, flash, url_for, session, current_app, jsonify
from flask_login import login_user, logout_user
import bcrypt

from dishdash.models.user import User
from dishdash.utils.helpers import EMAIL_REGEX, USERNAME_REGEX

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    users_collection = current_app.users_collection
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        if not email or not password:
            return redirect(url_for('auth.login'))

        user = users_collection.find_one({'email': email})
        if not user:
            flash('Incorrect email or password.', 'error')
            return redirect(url_for('auth.login'))
        
        if not bcrypt.checkpw(password.encode('utf-8'), user['password']):
            flash('Incorrect email or password.', 'error')
            return redirect(url_for('auth.login'))
        
        session['user_id'] = str(user['_id'])
        login_user(User(str(user['_id']), user['username']))
        return redirect(url_for('main.index'))

    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    users_collection = current_app.users_collection
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        if not EMAIL_REGEX.fullmatch(email):
            flash('Please enter a valid email address.', 'error')
            return redirect(url_for('auth.register'))
        
        if not USERNAME_REGEX.fullmatch(username):
            flash('Username must contain only letters, numbers, and underscores.', 'error')
            return redirect(url_for('auth.register'))

        password_clean = ''.join(password.split())
        if len(password_clean) < 8 or \
           not any(c.isupper() for c in password_clean) or \
           not any(c.isdigit() for c in password_clean) or \
           not any(not c.isalnum() for c in password_clean):
            return redirect(url_for('auth.register'))

        if users_collection.find_one({'username': username}):
            flash('Username already exists. Please choose a different one.', 'error')
            return redirect(url_for('auth.register'))

        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        users_collection.insert_one({
            'username': username,
            'email': email,
            'password': hashed_pw
        })

        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')

@auth_bp.route('/check_username', methods=['POST'])
def check_username():
    if not request.is_json:
        return jsonify({'error': 'Invalid request'}), 400
        
    username = request.json.get('username', '')
    users_collection = current_app.users_collection
    
    if users_collection.find_one({'username': username}):
        return jsonify({'available': False})
    return jsonify({'available': True})

@auth_bp.route('/check_email', methods=['POST'])
def check_email():
    if not request.is_json:
        return jsonify({'error': 'Invalid request'}), 400
        
    email = request.json.get('email', '')
    users_collection = current_app.users_collection
    
    if users_collection.find_one({'email': email}):
        return jsonify({'available': False})
    return jsonify({'available': True})

@auth_bp.route('/logout')
def logout():
    logout_user()
    session.pop('user_id', None)
    return redirect(url_for('main.index'))