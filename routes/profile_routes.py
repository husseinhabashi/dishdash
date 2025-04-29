import os
import re
from flask import Blueprint, render_template, request, redirect, url_for, current_app, flash, session
from flask_login import login_required, current_user, logout_user, login_user
from werkzeug.utils import secure_filename
from bson.objectid import ObjectId

from ..utils.helpers import allowed_file, get_current_user_document
from ..models.user import User

USERNAME_REGEX = re.compile(r'^[a-zA-Z0-9_]+$')

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    users_collection = current_app.users_collection
    user = get_current_user_document(users_collection)
    if not user:
        return redirect(url_for('auth.login'))

    profile_pic = user.get('profile_picture', 'default_picture.jpg')
    form_data = {}

    if request.method == 'POST':
        action = request.form.get("action")

        if action == "upload_image":
            file = request.files.get("profile-pic")
            if file and allowed_file(file.filename, current_app.config["ALLOWED_EXTENSIONS"]):
                ext = file.filename.rsplit('.', 1)[1].lower()
                new_filename = secure_filename(f"{user['username']}.{ext}")
                file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], new_filename)

                try:
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    file.save(file_path)

                    users_collection.update_one(
                        {'_id': user['_id']},
                        {'$set': {'profile_picture': new_filename}}
                    )
                    flash('Profile picture updated successfully!', 'success')
                except Exception as e:
                    print("profile_routes error: ", e)
                    flash('Error uploading profile picture', 'error')

            return redirect(url_for('profile.profile'))

        elif action == "save_profile":
            new_username = request.form.get("username", "").strip()
            form_data['username'] = new_username

            if new_username:
                if not USERNAME_REGEX.match(new_username):
                    flash('Username must contain only letters, numbers, and underscores.', 'error')
                    return render_template("profile.html", username=user["username"], 
                                          profile_pic=f"img/uploads/{profile_pic}", 
                                          form_data=form_data)
                
                existing_user = users_collection.find_one({'username': new_username})
                if existing_user and str(existing_user['_id']) != str(user['_id']):
                    flash('Username already exists. Please choose a different one.', 'error')
                    return render_template("profile.html", username=user["username"], 
                                          profile_pic=f"img/uploads/{profile_pic}", 
                                          form_data=form_data)
                
                result = users_collection.update_one(
                    {'_id': ObjectId(user['_id'])}, 
                    {'$set': {'username': new_username}}
                )
                
                if result.modified_count > 0:
                    logout_user()
                    updated_user = users_collection.find_one({'_id': ObjectId(user['_id'])})
                    login_user(User(str(updated_user['_id']), updated_user['username']))
                    flash('Username updated successfully!', 'success')
                else:
                    flash('No changes were made to username.', 'info')
            
            new_password = request.form.get("password", "").strip()
            if new_password:
                pass
                
            return redirect(url_for('profile.profile'))

    return render_template("profile.html", username=user["username"], profile_pic=f"img/uploads/{profile_pic}", form_data={})