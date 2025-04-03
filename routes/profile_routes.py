import os
from flask import Blueprint, render_template, request, redirect, url_for, current_app
from flask_login import login_required
from werkzeug.utils import secure_filename

from dishdash.utils.helpers import allowed_file, get_current_user_document

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    users_collection = current_app.users_collection
    user = get_current_user_document(users_collection)
    if not user:
        return redirect(url_for('auth.login'))

    profile_pic = user.get('profile_picture', 'default_picture.jpg')

    if request.method == 'POST':
        action = request.form.get("action")

        if action == "upload_image":
            file = request.files.get("profile-pic")
            if file and allowed_file(file.filename, current_app.config["ALLOWED_EXTENSIONS"]):
                ext = file.filename.rsplit('.', 1)[1].lower()
                new_filename = f"{user['username']}.{ext}"
                file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], new_filename)
                file.save(file_path)
                users_collection.update_one({'_id': user['_id']}, {'$set': {'profile_picture': new_filename}})
            return redirect(url_for('profile.profile'))

        elif action == "save_profile":
            new_username = request.form.get("username", "").strip()
            if new_username and not users_collection.find_one({'username': new_username, '_id': {'$ne': user['_id']}}):
                users_collection.update_one({'_id': user['_id']}, {'$set': {'username': new_username}})
            return redirect(url_for('profile.profile'))

    return render_template("profile.html", username=user["username"], profile_pic=f"img/uploads/{profile_pic}")