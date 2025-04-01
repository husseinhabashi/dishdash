import os
from dotenv import load_dotenv

load_dotenv()  # Loads values from .env file into environment variables

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    MONGO_URI = os.getenv("MONGO_URI")
    UPLOAD_FOLDER = "static/img/uploads/"
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

    @staticmethod
    def validate():
        if not Config.SECRET_KEY:
            raise ValueError("SECRET_KEY not set in .env")
        if not Config.MONGO_URI:
            raise ValueError("MONGO_URI not set in .env")