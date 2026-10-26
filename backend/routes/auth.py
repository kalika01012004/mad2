import re
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required
from models import db, User, Notification
from routes import get_current_user

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@auth_bp.route("/register", methods=["POST"])
def register_student():
    body = request.get_json() or {}
    role = (body.get("role") or "student").strip().lower()
    if role != "student":
        return jsonify({
            "error": "Registration is only open to students. Admin and examiners cannot register here."
        }), 403

    name = (body.get("name") or "").strip()
    email = (body.get("email") or "").strip().lower()
    username = (body.get("username") or "").strip().lower()
    password = body.get("password") or ""
    contact = (body.get("contact_details") or "").strip()
    dept = (body.get("department") or "Computer Science").strip()
    roll_no = (body.get("roll_number") or "").strip().upper()

    if not name or len(name) < 2:
        return jsonify({"error": "Name is required."}), 400
    if not email or not EMAIL_PATTERN.match(email):
        return jsonify({"error": "Valid email is required."}), 400
    if not username:
        username = email.split("@")[0]
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters."}), 400

    exists = User.query.filter((User.email == email) | (User.username == username)).first()
    if exists:
        return jsonify({"error": "Email or username already exists."}), 409

    student = User(
        name=name,
        email=email,
        username=username,
        role="student",
        contact_details=contact,
        department=dept,
        roll_number=roll_no,
        status="Active",
    )
    student.set_password(password)
    db.session.add(student)
    db.session.flush()

