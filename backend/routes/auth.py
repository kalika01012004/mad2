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

    if not student.roll_number:
        student.roll_number = f"26F{student.id:04d}"

    db.session.add(
        Notification(
            user_id=student.id,
            title="Welcome to EMP V2",
            message="Your student account is active. You can browse courses and book examination slots.",
            notif_type="system",
        )
    )
    db.session.commit()

    token = create_access_token(identity=str(student.id), additional_claims={"role": student.role})
    return jsonify({
        "message": "Student registered.",
        "access_token": token,
        "user": student.to_dict(),
    }), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    body = request.get_json() or {}
    raw_id = (body.get("identifier") or body.get("email") or body.get("username") or "").strip()
    if "(" in raw_id:
        raw_id = raw_id.split("(")[0].strip()
    ident = raw_id.lower()
