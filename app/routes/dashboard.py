from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from werkzeug.utils import secure_filename
import os
import app.services.academic_service as academic_service
from app.models import User, AcademicRequests
from app.decorators import active_required

dashboard = Blueprint("dashboard", __name__)

@dashboard.route("/dashboard")
@active_required
def user_dashboard():

    academic_requests = AcademicRequests.query.filter_by(email=session.get("email")).all()
    return render_template("dashboard.html", user = session["user"], email = session["email"], role = session["role"], academic_requests = academic_requests)

@dashboard.route("/dashboard/request_form")
@active_required
def request_form():
    # Get the form_id from query string parameters
    form_id = request.args.get("form_id", type=int)
    # For now, simply flash a message and render a simple template.
    if form_id == 1:
        flash("Academic Form 1 requested", "info")
        return redirect(url_for("dashboard.special_circumstance"))
    elif form_id == 2:
        flash("Academic Form 2 requested""info")
        return redirect(url_for("dashboard.course_drop"))
    else:
        flash("Invalid form selection", "error")
    # In a full implementation, you could pre-fill a form with user data or redirect to a dedicated form page.
    return redirect(url_for("dashboard.dashboard_home"))

@dashboard.route("/special_circumstance", methods=["GET", "POST"])
@active_required
def special_circumstance():
    if request.method == "POST":
        # Retrieve form values
        student_name = request.form.get("student_name")
        student_id = request.form.get("student_id")
        degree = request.form.get("degree")
        graduation_date = request.form.get("graduation_date")
        special_request_option = request.form.get("special_request_option")
        other_option_detail = request.form.get("other_option_detail")
        justification = request.form.get("justification")

        signature_file = request.files.get("signature")
        signature_filename = None
        if signature_file:
            from werkzeug.utils import secure_filename
            # Optionally, validate file extension if needed
            signature_filename = secure_filename(signature_file.filename)
            # Save file to 'app/static/uploads' folder (ensure the folder exists)
            upload_folder = os.path.join("app", "static", "uploads")
            # Create the folder if it doesn't exist
            os.makedirs(upload_folder, exist_ok=True)
            upload_path = os.path.join(upload_folder, signature_filename)
            signature_file.save(upload_path)

        request_data = {
            "student_name": student_name,
            "student_id": student_id,
            "degree": degree,
            "graduation_date": graduation_date,
            "special_request_option": special_request_option,
            "other_option_detail": other_option_detail,
            "justification": justification,
            "signature": signature_filename  # store file name
        }

        # Determine whether to save as draft or submit
        action = request.form.get("action")
        if action == "save_draft":
            status = "draft"
        else:
            status = "under_review"  # or "pending", as per your business logic

        academic_service.submit_form(request_data, 1, status)
        if status == "draft":
            flash("Draft saved succesfully.", "success")
        else:
            flash("Form submitted succesfully.", "success")

    return render_template("special_circumstance.html")


@dashboard.route("/special_circumstance/edit/<int:request_id>", methods=["GET", "POST"])
@active_required
def special_circumstance(request_id):
    if request.method == "POST":
        draft["student_name"] = request.form.get("student_name")
        draft["student_id"] = request.form.get("student_id")
        draft["degree"] = request.form.get("degree")
        draft["graduation_date"] = request.form.get("graduation_date")
        draft["special_request_option"] = request.form.get("special_request_option")
        draft["other_option_detail"] = request.form.get("other_option_detail")
        draft["justification"] = request.form.get("justification")

        # Process new signature file upload if provided
        signature_file = request.files.get("signature")
        if signature_file:
            from werkzeug.utils import secure_filename
            signature_filename = secure_filename(signature_file.filename)
            upload_folder = os.path.join("app", "static", "uploads")
            os.makedirs(upload_folder, exist_ok=True)
            signature_file.save(os.path.join(upload_folder, signature_filename))
            draft["signature_filename"] = signature_filename

        academic_service.update_form(id, draft)
        flash("Form updated succesfully.", "success")

    return render_template("special_circumstance.html")


#TODO: Change the endpoints
@dashboard.route("/course_drop", methods=["GET", "POST"])
@active_required
def course_drop():
    if request.method == "POST":
        # Retrieve form values
        student_name = request.form.get("student_name")
        student_id = request.form.get("student_id")
        course_subject = request.form.get("course_subject")
        course_number = request.form.get("course_number")
        semester = request.form.get("semester")
        year = request.form.get("year")

        signature_file = request.files.get("signature")
        signature_filename = None
        if signature_file:
            from werkzeug.utils import secure_filename
            # Optionally, validate file extension if needed
            signature_filename = secure_filename(signature_file.filename)
            # Save file to 'app/static/uploads' folder (ensure the folder exists)
            upload_folder = os.path.join("app", "static", "uploads")
            # Create the folder if it doesn't exist
            os.makedirs(upload_folder, exist_ok=True)
            upload_path = os.path.join(upload_folder, signature_filename)
            signature_file.save(upload_path)

        request_data = {
            "student_name": student_name,
            "student_id": student_id,
            "course_subject": course_subject,
            "course_number": course_number,
            "semester": semester,
            "year": year,
            "signature": signature_filename  # store file name
        }

        # Determine whether to save as draft or submit
        action = request.form.get("action")
        if action == "save_draft":
            status = "draft"
        else:
            status = "under_review"  # or "pending", as per your business logic

        academic_service.submit_form(request_data, 2, status)
        if status == "draft":
            flash("Draft saved succesfully.", "success")
        else:
            flash("Form submitted succesfully.", "success")

    return render_template("course_drop.html")

@dashboard.route("/dashboard/special_circumstance/edit/<int:request_id>", methods=["GET", "POST"])
@active_required
def special_circumstance(request_id):
    if request.method == "POST":
        draft["student_name"] = request.form.get("student_name")
        draft["student_id"] = request.form.get("student_id")
        draft["course_subject"] = request.form.get("course_subject")
        draft["course_number"] = request.form.get("course_number")
        draft["semester"] = request.form.get("semester")
        draft["year"] = request.form.get("year")

        # Process new signature file upload if provided
        signature_file = request.files.get("signature")
        if signature_file:
            from werkzeug.utils import secure_filename
            signature_filename = secure_filename(signature_file.filename)
            upload_folder = os.path.join("app", "static", "uploads")
            os.makedirs(upload_folder, exist_ok=True)
            signature_file.save(os.path.join(upload_folder, signature_filename))
            draft["signature_filename"] = signature_filename

        academic_service.update_form(id, draft)
        flash("Form updated succesfully.", "success")

    return render_template("special_circumstance.html")

@dashboard.route("/dashboard/delete_form/<int:request_id>", methods=["POST"])
@active_required
def delete_form(request_id):
    # Query for the request; ensure it belongs to the logged-in student
    draft = AcademicRequest.query.filter_by(id=request_id, student_email=session.get("email")).first_or_404()
    
    # Delete the draft and commit changes
    db.session.delete(draft)
    db.session.commit()
    
    flash("Your request has been deleted.", "success")
    return redirect(url_for("dashboard.dashboard_home"))



