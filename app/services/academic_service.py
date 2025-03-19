from flask import session
from app.models import AcademicRequests
from app.extensions.db import db

def get_all_forms():
    pass

#form_type = 1 -> special circumstance
def submit_form(data, form_type, status):
    new_request = AcademicRequests(
        email=session.get("email"),
        form_type=1,
        data=data,
        status=status
    )
    db.session.add(new_request)
    db.session.commit()

def update_form(id, form_type, updated_data):
    draft = AcademicRequest.query.filter_by(id=id, student_email=session.get("email")).first_or_404()
    # Update fields from the form submission
    if form_type == 1:
        draft.student_name = updated_data["student_name"]
        draft.student_id = updated_data["student_id"] 
        draft.degree =  updated_data["degree"] 
        draft.graduation_date =  updated_data["graduation_date"] 
        draft.special_request_option =  updated_data["special_request_option"] 
        draft.other_option_detail =  updated_data["other_option_detail"] 
        draft.justification =  updated_data["justification"] 

    if form_type == 2:
        draft.student_name =  updated_data["student_name"] 
        draft.student_id =  updated_data["student_id"] 
        draft.course_name =  updated_data["course_name"] 
        draft.course_number =  updated_data["course_number"] 
        draft.semester =  updated_data["semester"] 
        draft.year =  updated_data["year"] 


    # Process new signature file upload if provided
    signature_file = request.files.get("signature")
    if signature_file:
        from werkzeug.utils import secure_filename
        signature_filename = secure_filename(signature_file.filename)
        upload_folder = os.path.join("app", "static", "uploads")
        os.makedirs(upload_folder, exist_ok=True)
        signature_file.save(os.path.join(upload_folder, signature_filename))
        draft.signature_filename = signature_filename

    db.session.commit()

def delete_form(id):
    draft = AcademicRequest.query.filter_by(id=id, student_email=session.get("email")).first_or_404()
    
    # Delete the draft and commit changes
    db.session.delete(draft)
    db.session.commit()


