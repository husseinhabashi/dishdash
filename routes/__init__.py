from .auth_routes import auth_bp
from .main_routes import main_bp
from .profile_routes import profile_bp

def register_routes(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(profile_bp)