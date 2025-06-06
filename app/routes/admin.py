from flask import Blueprint, render_template, session, redirect, url_for, flash, request, current_app, send_file
import app.services.user_service as user_service
from app.models import User
from app.decorators import admin_required, active_required
from app.models import AcademicRequests
from app.extensions.db import db
import json
import os
import subprocess
import shutil
import base64
import app.services.workflow_service as workflow_service
from app.models import ApprovalWorkflow, WorkflowStep



admin = Blueprint("admin", __name__)

@admin.route("/admin/dashboard")
@admin_required
@active_required
def admin_dashboard():
    if "user" not in session:
        flash("Please log in to access the dashboard", "error")
        return redirect(url_for("auth.microsoft_login"))

    # Restrict access to Admins only
    #if session.get("role") != "Admin":
    #    flash("Access Denied: Admins Only!", "error")
    #    return redirect(url_for("main.home"))

    # Temporary Hardcoded Users (Replace with Database Query Later)
    #users = [
    #    {"id": 1, "name": "Alice", "email": "alice@example.com", "role": "User", "status": "Active"},
    #    {"id": 2, "name": "Bob", "email": "bob@example.com", "role": "Admin", "status": "Active"},
    #]

    users = user_service.get_all_users()

    return render_template("admin.html", user=session["user"], email=session["email"], role=session["role"], users=users)


@admin.route("/admin/update_user/<int:user_id>", methods = ["GET", "POST"])
@admin_required
@active_required
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        # Retrieve form data. Only update if a value is provided.
        new_display_name = request.form.get('display_name')
        new_email = request.form.get('email')
        new_role = request.form.get('role')
        new_status = request.form.get('status')

        # Track what was updated for the flash message
        updated_fields = []

        if new_display_name and new_display_name != user.display_name:
            user.display_name = new_display_name
            updated_fields.append("display name")
        if new_email and new_email != user.email:
            user.email = new_email
            updated_fields.append("email")
        if new_role and new_role != user.role:
            user.role = new_role
            updated_fields.append("role")
        if new_status and new_status != user.status:
            user.status = new_status
            updated_fields.append("status")

        user_service.update_user(user)
        
        if updated_fields:
            flash(f"User information updated successfully! (Updated: {', '.join(updated_fields)})", "success")
        else:
            flash("No changes were made to the user information.", "info")
            
        return redirect(url_for('admin.admin_dashboard'))
    # If GET, render the update form with current user data pre-filled
    return render_template('admin_update.html', user=user)

@admin.route("/admin/delete_user/<int:user_id>", methods = ["POST"])
@admin_required
@active_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    user_service.delete_user(user)
    flash("User deleted successfully!", "success")
    return redirect(url_for('admin.admin_dashboard'))

@admin.route("/admin/create_user", methods = ["POST"])
@admin_required
@active_required
def create_user():
    # Get data from the form submission
    display_name = request.form.get('display_name')
    email = request.form.get('email')
    role = request.form.get('role', 'User')
    status = request.form.get('status', 'active')

    # Validate required fields
    if not display_name or not email:
        flash("Name and Email are required.", "error")
        return redirect(url_for('admin.admin_dashboard'))

    # Create a new User instance
    user_service.create_user(display_name, email, role, status)
    #new_user = User(display_name=display_name, email=email, role=role, status=status)

    flash("User created successfully!", "success")
    return redirect(url_for('admin.admin_dashboard'))


@admin.route("/admin/review_requests")
@admin_required
@active_required
def review_requests():
    # Fetch all submitted requests (not drafts)
    requests = AcademicRequests.query.filter(AcademicRequests.status != "draft").all()
    return render_template("review_requests.html", requests=requests)



@admin.route("/admin/view_request/<int:request_id>")
@admin_required
def view_request(request_id):
    req = AcademicRequests.query.get_or_404(request_id)
    temp_dir = os.path.join(current_app.instance_path, "temp")
    os.makedirs(temp_dir, exist_ok=True)

    # Create a copy of the data to modify
    request_data = req.data.copy() if req.data else {}
    
    # Handle signature if it exists
    if "signature" in request_data and request_data["signature"]:
        try:
            # Create a unique filename for this signature
            signature_image_filename = f"signature_view_{request_id}.png"
            signature_image_path = os.path.join(temp_dir, signature_image_filename)
            
            # Remove file if it already exists
            if os.path.exists(signature_image_path):
                os.remove(signature_image_path)
                
            # Decode the Base64 string into binary data
            signature_binary = base64.b64decode(request_data["signature"])
            
            # Write image data to file
            with open(signature_image_path, "wb") as img_file:
                img_file.write(signature_binary)
                
            # Add path for display in the view
            request_data["signature_image_path"] = url_for("static", filename=f"../instance/temp/{signature_image_filename}")
        except Exception as e:
            current_app.logger.error(f"Error processing signature for view: {e}")
            request_data["signature_image_path"] = None
    else:
        request_data["signature_image_path"] = None

    return render_template("view_request.html", request=req, form_data=request_data)

@admin.route("/admin/approve_request/<int:request_id>", methods=["POST"])
@admin_required
def approve_request(request_id):
    req = AcademicRequests.query.get_or_404(request_id)
    req.status = "approved"
    db.session.commit()
    flash("Request approved!", "success")
    return redirect(url_for("admin.review_requests"))

@admin.route("/admin/reject_request/<int:request_id>", methods=["POST"])
@admin_required
def reject_request(request_id):
    req = AcademicRequests.query.get_or_404(request_id)
    req.status = "rejected"
    db.session.commit()
    flash("Request rejected!", "danger")
    return redirect(url_for("admin.review_requests"))

@admin.route("/admin/view_pdf/<int:request_id>", methods=["GET"])
@active_required
@admin_required
def view_pdf(request_id):
    draft = AcademicRequests.query.filter_by(id=request_id).first_or_404()
    request_data = draft.data.copy()
    temp_dir = os.path.join(current_app.instance_path, "temp")
    os.makedirs(temp_dir, exist_ok=True)

    # Debug prints
    print("Admin view - Request data keys:", request_data.keys())
    
    # Handle signature if it exists
    if "signature" in request_data and request_data["signature"]:
        print("Admin view - Signature found in request data")
        # Create a unique filename for this signature
        signature_image_filename = f"signature_{request_id}.png"
        signature_image_path = os.path.join(temp_dir, signature_image_filename)
        
        try:
            # Remove file if it already exists
            if os.path.exists(signature_image_path):
                os.remove(signature_image_path)
                
            # Decode the Base64 string into binary data
            signature_binary = base64.b64decode(request_data["signature"])
            print(f"Admin view - Decoded signature length: {len(signature_binary)} bytes")
            
            # Write image data to file
            with open(signature_image_path, "wb") as img_file:
                img_file.write(signature_binary)
            
            print(f"Admin view - Signature saved to: {signature_image_path}")
            
            # Set the image path for the template - just use the filename, not the full path
            request_data["signature_image_filename"] = signature_image_filename
        except Exception as e:
            current_app.logger.error(f"Admin view - Error processing signature image: {e}")
            print(f"Admin view - Error processing signature: {e}")
            request_data["signature_image_filename"] = None
    else:
        print("Admin view - No signature data found in the request")
        request_data["signature_image_filename"] = None

    # Copy signature to LaTeX working directory if it exists
    if request_data.get("signature_image_filename"):
        # Ensure the signature is in the same directory as the .tex file for simpler inclusion
        signature_source = os.path.join(temp_dir, request_data["signature_image_filename"])
        if os.path.exists(signature_source):
            print(f"Admin view - File exists at {signature_source}")
        else:
            print(f"Admin view - File does not exist: {signature_source}")

    # Generate appropriate template based on form type
    if draft.form_type == 1: 
        rendered_tex = render_template("special_circumstance.tex.j2", request_data=request_data)
        tex_file = os.path.join(temp_dir, "special_circumstance.tex")
        pdf_file = os.path.join(temp_dir, "special_circumstance.pdf")
    elif draft.form_type == 2:
        rendered_tex = render_template("course_drop.tex.j2", request_data=request_data)
        tex_file = os.path.join(temp_dir, "course_drop.tex")
        pdf_file = os.path.join(temp_dir, "course_drop.pdf")
    elif draft.form_type == 3:
        rendered_tex = render_template("affidavit_intent.tex.j2", request_data=request_data)
        tex_file = os.path.join(temp_dir, "affidavit_intent.tex")
        pdf_file = os.path.join(temp_dir, "affidavit_intent.pdf")
    elif draft.form_type == 4:
        rendered_tex = render_template("tuition_exemption.tex.j2", request_data=request_data)
        tex_file = os.path.join(temp_dir, "tuition_exemption.tex")
        pdf_file = os.path.join(temp_dir, "tuition_exemption.pdf")
    else:
        rendered_tex = render_template("course_drop.tex.j2", request_data=request_data)
        tex_file = os.path.join(temp_dir, "course_drop.tex")
        pdf_file = os.path.join(temp_dir, "course_drop.pdf")
    
    # Write the rendered LaTeX to a file
    with open(tex_file, "w") as f:
        f.write(rendered_tex)
    
    # Print LaTeX content for debugging
    print("Admin view - Generated LaTeX content:")
    print(rendered_tex[:200] + "...")
    
    # Compile the .tex file into a PDF using pdflatex.
    try:
        makefile_src = os.path.join(current_app.root_path, "latex", "Makefile")
        makefile_dst = os.path.join(temp_dir, "Makefile")
        shutil.copy(makefile_src, makefile_dst)
        
        # Run compilation commands
        print("Admin view - Running make clean")
        subprocess.run(["make", "-C", temp_dir, "clean"], check=True)
        
        if draft.form_type == 2:
            print("Admin view - Compiling course_drop.pdf")
            result = subprocess.run(["make", "-C", temp_dir, "course_drop.pdf"], check=True, capture_output=True, text=True)
            if result.stderr:
                print(f"Admin view - Compilation errors: {result.stderr}")
            
            # Run twice for references
            subprocess.run(["make", "-C", temp_dir, "course_drop.pdf"], check=True)
        elif draft.form_type == 3:
            print("Admin view - Compiling affidavit_intent.pdf")
            result = subprocess.run(["make", "-C", temp_dir, "affidavit_intent.pdf"], check=True, capture_output=True, text=True)
            if result.stderr:
                print(f"Admin view - Compilation errors: {result.stderr}")
            
            # Run twice for references
            subprocess.run(["make", "-C", temp_dir, "affidavit_intent.pdf"], check=True)
        elif draft.form_type == 4:
            print("Admin view - Compiling tuition_exemption.pdf")
            result = subprocess.run(["make", "-C", temp_dir, "tuition_exemption.pdf"], check=True, capture_output=True, text=True)
            if result.stderr:
                print(f"Admin view - Compilation errors: {result.stderr}")
            
            # Run twice for references
            subprocess.run(["make", "-C", temp_dir, "tuition_exemption.pdf"], check=True)
        else:
            print("Admin view - Compiling special_circumstance.pdf")
            result = subprocess.run(["make", "-C", temp_dir, "special_circumstance.pdf"], check=True, capture_output=True, text=True)
            if result.stderr:
                print(f"Admin view - Compilation errors: {result.stderr}")
            
            # Run twice for references
            subprocess.run(["make", "-C", temp_dir, "special_circumstance.pdf"], check=True)
        
        print("Admin view - PDF compilation completed successfully")
    except subprocess.CalledProcessError as e:
        current_app.logger.error(f"Admin view - Error compiling PDF: {e}")
        print(f"Admin view - PDF compilation failed: {e}")
        flash("Error generating PDF.", "error")
        return redirect(url_for("admin.review_requests"))
    
    # Return the generated PDF as a response.
    return send_file(pdf_file, mimetype="application/pdf", as_attachment=False)

@admin.route("/admin/workflows")
@admin_required
def manage_workflows():
    """View and manage approval workflows"""
    workflows = workflow_service.get_all_workflows()
    return render_template("admin/workflows.html", workflows=workflows)

@admin.route("/admin/workflows/new", methods=["GET", "POST"])
@admin_required
def new_workflow():
    """Create a new workflow"""
    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        
        if not name:
            flash("Workflow name is required", "error")
            return render_template("admin/workflow_form.html")
        
        # Check if a workflow with this name already exists
        existing_workflow = ApprovalWorkflow.query.filter_by(name=name).first()
        if existing_workflow:
            flash(f"A workflow with the name '{name}' already exists", "error")
            return render_template("admin/workflow_form.html")
        
        try:
            workflow_id = workflow_service.create_workflow(name, description)
            flash(f"Workflow '{name}' created successfully", "success")
            return redirect(url_for("admin.edit_workflow", workflow_id=workflow_id))
        except Exception as e:
            flash(f"Error creating workflow: {str(e)}", "error")
            current_app.logger.error(f"Error creating workflow: {e}")
            return render_template("admin/workflow_form.html")
    
    return render_template("admin/workflow_form.html")

@admin.route("/admin/workflows/<int:workflow_id>", methods=["GET", "POST"])
@admin_required
def edit_workflow(workflow_id):
    """Edit a workflow and its steps"""
    workflow = workflow_service.get_workflow_by_id(workflow_id)
    steps = workflow_service.get_workflow_steps(workflow_id)
    
    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        is_active = request.form.get("is_active") == "on"
        
        if not name:
            flash("Workflow name is required", "error")
            return render_template("admin/workflow_form.html", workflow=workflow, steps=steps)
        
        # Check if a workflow with this name already exists (excluding the current one)
        existing_workflow = ApprovalWorkflow.query.filter(
            ApprovalWorkflow.name == name, 
            ApprovalWorkflow.id != workflow_id
        ).first()
        
        if existing_workflow:
            flash(f"A workflow with the name '{name}' already exists", "error")
            return render_template("admin/workflow_form.html", workflow=workflow, steps=steps)
        
        try:
            workflow_service.update_workflow(workflow_id, name, description, is_active)
            flash(f"Workflow '{name}' updated successfully", "success")
            return redirect(url_for("admin.manage_workflows"))
        except Exception as e:
            flash(f"Error updating workflow: {str(e)}", "error")
            current_app.logger.error(f"Error updating workflow: {e}")
            return render_template("admin/workflow_form.html", workflow=workflow, steps=steps)
    
    return render_template("admin/workflow_form.html", workflow=workflow, steps=steps)

@admin.route("/admin/workflows/<int:workflow_id>/delete", methods=["POST"])
@admin_required
def delete_workflow(workflow_id):
    """Delete a workflow"""
    success, message = workflow_service.delete_workflow(workflow_id)
    
    if success:
        flash(message, "success")
    else:
        flash(message, "error")
    
    return redirect(url_for("admin.manage_workflows"))

@admin.route("/admin/workflows/<int:workflow_id>/steps/add", methods=["POST"])
@admin_required
def add_workflow_step(workflow_id):
    """Add a step to a workflow"""
    role = request.form.get("role")
    step_order = request.form.get("step_order", type=int)
    can_skip = request.form.get("can_skip") == "on"
    is_required = request.form.get("is_required") == "on"
    
    if not role or step_order is None:
        flash("Role and step order are required", "error")
        return redirect(url_for("admin.edit_workflow", workflow_id=workflow_id))
    
    success, message = workflow_service.add_workflow_step(workflow_id, role, step_order, can_skip, is_required)
    
    if success:
        flash(message, "success")
    else:
        flash(message, "error")
    
    return redirect(url_for("admin.edit_workflow", workflow_id=workflow_id))

@admin.route("/admin/workflows/steps/<int:step_id>/update", methods=["POST"])
@admin_required
def update_workflow_step(step_id):
    """Update a workflow step"""
    step = WorkflowStep.query.get_or_404(step_id)
    workflow_id = step.workflow_id
    
    role = request.form.get("role")
    step_order = request.form.get("step_order", type=int)
    can_skip = request.form.get("can_skip") == "on"
    is_required = request.form.get("is_required") == "on"
    
    success, message = workflow_service.update_workflow_step(step_id, role, step_order, can_skip, is_required)
    
    if success:
        flash(message, "success")
    else:
        flash(message, "error")
    
    return redirect(url_for("admin.edit_workflow", workflow_id=workflow_id))

@admin.route("/admin/workflows/steps/<int:step_id>/delete", methods=["POST"])
@admin_required
def delete_workflow_step(step_id):
    """Delete a workflow step"""
    step = WorkflowStep.query.get_or_404(step_id)
    workflow_id = step.workflow_id
    
    success, message = workflow_service.delete_workflow_step(step_id)
    
    if success:
        flash(message, "success")
    else:
        flash(message, "error")
    
    return redirect(url_for("admin.edit_workflow", workflow_id=workflow_id))


