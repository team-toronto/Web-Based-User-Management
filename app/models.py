from datetime import datetime, timezone, timedelta
from .extensions.db import db
#from flask_login import UserMixin

class User(db.Model):
    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    display_name = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(50), default="User")
    status = db.Column(db.String(50), default="active")

    def __repr__(self):
        return f"<User {self.email}>"

class AcademicRequests(db.Model):
    __tablename__ = "academic_requests"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(120), nullable=False)
    form_type = db.Column(db.Integer, nullable=False)  # e.g., "Transcript Request", etc.
    data = db.Column(db.JSON, nullable=False)             # JSON/text containing form data
    status = db.Column(db.String(20), default="draft")      # draft, pending, returned, approved, etc.
    created_at = db.Column(db.DateTime, default = lambda: datetime.now(timezone(-timedelta(hours=5)).utc))

    def __repr__(self):
        return f"<AcademicRequest {self.id} for {self.email}>"
