from flask_login import UserMixin
from bson.objectid import ObjectId

class User(UserMixin):
    def __init__(self, user_id, username):
        self.id = user_id
        self.username = username

    @staticmethod
    def get(users_collection, user_id):
        try:
            user = users_collection.find_one({"_id": ObjectId(user_id)})
            if user:
                return User(str(user["_id"]), user["username"])
        except Exception as e:
            print(f"User fetch error: {e}")
        return None