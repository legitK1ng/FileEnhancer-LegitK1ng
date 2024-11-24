import os
import os
from datetime import timedelta
from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
from flask_mail import Mail
mail = Mail()
login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ.get("FLASK_SECRET_KEY") or os.urandom(24)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024 * 1024  # 10GB
    # Email Configuration
    app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER')
    app.config['UPLOAD_CHUNK_SIZE'] = 1024 * 1024  # 1MB chunks
    app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')
    app.config['TEMP_FOLDER'] = os.path.join(os.getcwd(), 'uploads', 'temp')
    
    # Create upload and temp directories
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['TEMP_FOLDER'], exist_ok=True)
    app.config["SESSION_COOKIE_SECURE"] = True
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=7)
    app.config["REMEMBER_COOKIE_DURATION"] = timedelta(days=7)
    app.config["REMEMBER_COOKIE_SECURE"] = True
    app.config["REMEMBER_COOKIE_HTTPONLY"] = True

    db.init_app(app)
    mail.init_app(app)
    
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    with app.app_context():
        import models
        db.create_all()

        from routes.auth import auth_bp
        from routes.files import files_bp
        from routes.processing import processing_bp
        from routes.google_auth import google_bp

        app.register_blueprint(auth_bp)
        app.register_blueprint(files_bp)
        app.register_blueprint(processing_bp)
        app.register_blueprint(google_bp)

    return app
