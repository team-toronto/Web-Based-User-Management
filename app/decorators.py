from functools import wraps
from flask import session, abort, flash, redirect, url_for
from app.models import User

#TODO: Reduce db lookups by utilizing session tags.
#TODO: Create a seperate wrapper for users not in database
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("role") != "Admin":
            abort(403)  # Forbidden
        return f(*args, **kwargs)
    return decorated_function


def active_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Ensure the user is logged in (assuming their email is stored in the session)
        if "email" not in session:
            flash("Please log in to access this page.", "error")
            return redirect(url_for("main.home"))

        # Query the database for the user using their email
        user = User.query.filter_by(email=session["email"].lower()).first()
        if not user:
            flash("User not found. Please log in again.", "error")
            return redirect(url_for("main.home"))

        # Check if the user is active
        if user.status.lower() != "active":
            flash("Your account is not active. Please contact support.", "error")
            return redirect(url_for("main.home"))

        return f(*args, **kwargs)
    return decorated_function
