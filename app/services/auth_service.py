import os
import requests
from flask import session, request
from app.models import User

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
TENANT_ID = os.getenv("TENANT_ID")
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/authorize"
TOKEN_URL = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
SCOPE = ["User.Read"]

def microsoft_callback(redirect_uri):

    code = request.args.get("code")
    if not code:
        return "main.home", "Login Failed, No authorization code."

    token_data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
        "scope": " ".join(SCOPE),
    }

    response = requests.post(TOKEN_URL, data=token_data)
    token_json = response.json()

    if "access_token" not in token_json:
        return "main.home", "Failed to authenticate with Microsoft"

    access_token = token_json["access_token"]
    session["access_token"] = access_token

    user_info = requests.get("https://graph.microsoft.com/v1.0/me", headers={"Authorization": f"Bearer {access_token}"}).json()

    session["user"] = user_info.get("displayName", "Unknown User")
    session["email"] = user_info.get("mail", "No Email Provided")
    session["exists"] = True
    session["active"] = True

    return user_info, "yipee"


