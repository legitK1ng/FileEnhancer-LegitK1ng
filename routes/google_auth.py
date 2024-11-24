import json
import os
from flask import Blueprint, redirect, request, url_for
from flask_login import login_user, logout_user, login_required
from oauthlib.oauth2 import WebApplicationClient
import requests
from models import User, db

GOOGLE_CLIENT_ID = os.environ["GOOGLE_OAUTH_CLIENT_ID"]
GOOGLE_CLIENT_SECRET = os.environ["GOOGLE_OAUTH_CLIENT_SECRET"]
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

google_bp = Blueprint('google_auth', __name__)
client = WebApplicationClient(GOOGLE_CLIENT_ID)

@google_bp.route('/login/google')
def google_login():
    google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url.replace("http://", "https://") + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)

@google_bp.route('/login/google/callback')
def google_callback():
    code = request.args.get("code")
    google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
    token_endpoint = google_provider_cfg["token_endpoint"]

    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url.replace("http://", "https://"),
        redirect_url=request.base_url.replace("http://", "https://"),
        code=code,
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    client.parse_request_body_response(json.dumps(token_response.json()))
    
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)
    
    userinfo = userinfo_response.json()
    if not userinfo.get("email_verified"):
        return "User email not verified by Google.", 400

    user = User.query.filter_by(email=userinfo["email"]).first()
    if not user:
        user = User(
            username=userinfo.get("name", "Google User"),
            email=userinfo["email"],
            google_id=userinfo["sub"],
            google_profile_pic=userinfo.get("picture"),
            google_email_verified=True
        )
        db.session.add(user)
        db.session.commit()
    else:
        user.google_id = userinfo["sub"]
        user.google_profile_pic = userinfo.get("picture")
        user.google_email_verified = True
        db.session.commit()

    login_user(user)
    return redirect(url_for('files.index'))
