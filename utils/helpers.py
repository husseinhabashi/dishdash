import re
from flask import session
from flask_login import current_user
from bson.objectid import ObjectId

EMAIL_REGEX = re.compile(r'\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b', re.IGNORECASE)
USERNAME_REGEX = re.compile(r'^[A-Za-z0-9_]+$')

def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def get_current_user_document(users_collection):
    try:
        user_id = current_user.id if current_user.is_authenticated else session.get("user_id")
        return users_collection.find_one({"_id": ObjectId(user_id)})
    except Exception as e:
        print(f"Error fetching user doc: {e}")
    return None