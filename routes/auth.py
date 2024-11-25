from datetime import datetime
from flask import Blueprint, request, redirect, url_for, render_template, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
from models import User, db
from datetime import datetime, timedelta
import secrets
import os

mail = Mail()

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember', False)
        
        if not email or not password:
            return render_template('login.html', error="Please fill in all fields")
            
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            if not user.email_verified:
                return render_template('login.html', 
                                     error="Please verify your email before logging in")
            login_user(user, remember=remember)
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            return redirect(url_for('files.index'))
            
        return render_template('login.html', error="Invalid email or password")
    
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(email=email).first():
            return render_template('register.html', error="Email already exists")
            
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
@auth_bp.route('/auth/replit')
def replit_auth():
    replit_user_id = request.headers.get('X-Replit-User-Id')
    replit_user_name = request.headers.get('X-Replit-User-Name')
    
    if not replit_user_id or not replit_user_name:
        return jsonify({'error': 'Missing Replit authentication headers'}), 401
        
    # Find or create user
    user = User.query.filter_by(replit_user_id=replit_user_id).first()
    if not user:
        # Create new user
        user = User(
            username=replit_user_name,
            email=f"{replit_user_id}@repl.user",  # Placeholder email
            replit_user_id=replit_user_id
        )
        db.session.add(user)
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.session.commit()
    
    # Log in the user
    login_user(user)
    
    return redirect(url_for('files.index'))

    return render_template('register.html')

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            token = secrets.token_urlsafe(32)
            user.password_reset_token = token
            user.token_expiry = datetime.utcnow() + timedelta(hours=1)
            db.session.commit()
            
            reset_url = url_for('auth.reset_password', token=token, _external=True)
            msg = Message('Reset Your Password',
                         sender=current_app.config['MAIL_DEFAULT_SENDER'],
                         recipients=[user.email])
            msg.html = render_template('email_templates/password_reset.html',
                                    reset_url=reset_url)
            mail.send(msg)
            return render_template('forgot_password.html',
                                success="Password reset instructions have been sent to your email")
        return render_template('forgot_password.html',
                            error="Email address not found")
    return render_template('forgot_password.html')

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    user = User.query.filter_by(password_reset_token=token).first()
    if not user or not user.token_expiry or user.token_expiry < datetime.utcnow():
        return render_template('login.html', error="Invalid or expired reset link")
        
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            return render_template('reset_password.html', error="Passwords do not match")
            
        user.password_hash = generate_password_hash(password)
        user.password_reset_token = None
        user.token_expiry = None
        db.session.commit()
        
        return redirect(url_for('auth.login'))
        
    return render_template('reset_password.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
