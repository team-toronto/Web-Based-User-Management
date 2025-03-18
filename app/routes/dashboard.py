from flask import Blueprint, render_template, session, redirect, url_for, flash, request
import app.services.user_service as user_service
from app.models import User
from app.decorators import active_required

dashboard = Blueprint("dashboard", __name__)

@dashboard.route("/dashboard")
@active_required
def user_dashboard():

    return render_template("dashboard.html", user=session["user"], email=session["email"], role=session["role"])
