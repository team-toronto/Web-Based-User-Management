from flask import session
from app.models import AcademicRequests
from app.extensions.db import db

def get_all_forms():
    pass

#form_type = 1 -> special circumstance
def submit_form(data, form_type, status):
    new_request = AcademicRequests(
        email=session.get("email"),
        form_type="Special Circumstance",
        data=data,
        status=status
    )
    db.session.add(new_request)
    db.session.commit()

def update_user(user):
    pass

def delete_user(user):
    pass


