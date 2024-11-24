from datetime import datetime
from app import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=True)
    google_id = db.Column(db.String(256), unique=True, nullable=True)
    google_profile_pic = db.Column(db.String(512), nullable=True)
    google_email_verified = db.Column(db.Boolean, default=False)
    password_reset_token = db.Column(db.String(64), unique=True, nullable=True)
    token_expiry = db.Column(db.DateTime, nullable=True)
    files = db.relationship('File', backref='owner', lazy=True)

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(512), nullable=False)
    filetype = db.Column(db.String(50))
    size = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    file_metadata = db.relationship('FileMetadata', backref='file', lazy=True)

class FileMetadata(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_id = db.Column(db.Integer, db.ForeignKey('file.id'), nullable=False)
    transcript = db.Column(db.Text)
    sentiment_score = db.Column(db.Float)
    entities = db.Column(db.JSON)
    speakers = db.Column(db.JSON)
    processed_at = db.Column(db.DateTime, default=datetime.utcnow)
