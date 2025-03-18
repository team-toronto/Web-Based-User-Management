from flask import Blueprint, render_template, session, redirect, url_for, flash, request
import app.services.user_service as user_service
from app.models import User, AcademicRequests
from app.decorators import active_required

dashboard = Blueprint("dashboard", __name__)

@dashboard.route("/dashboard")
@active_required
def user_dashboard():

    academic_requests = AcademicRequests.query.filter_by(email=session.get("email")).all()
    return render_template("dashboard.html", user=session["user"], email=session["email"], role=session["role"])

@dashboard.route("/dashboard/request_form")
@active_required
def request_form():
    # Get the form_id from query string parameters
    form_id = request.args.get("form_id", type=int)
    # For now, simply flash a message and render a simple template.
    if form_id == 1:
        flash("Academic Form 1 requested", "info")
    elif form_id == 2:
        flash("Academic Form 2 requested", "info")
    else:
        flash("Invalid form selection", "error")
    # In a full implementation, you could pre-fill a form with user data or redirect to a dedicated form page.
    return redirect(url_for("dashboard.dashboard_home"))

