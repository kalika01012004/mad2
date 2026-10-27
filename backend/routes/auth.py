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
    pwd = body.get("password") or ""

    if not ident or not pwd:
        return jsonify({"error": "Username/email and password are required."}), 400

    usr = User.query.filter(
        (db.func.lower(User.email) == ident)
        | (db.func.lower(User.username) == ident)
        | (db.func.lower(User.name) == ident)
        | (db.func.lower(User.roll_number) == ident)
    ).first()

    valid_pwd = False
    if usr and (usr.check_password(pwd) or usr.check_password(pwd.strip())):
        valid_pwd = True

    if not usr or not valid_pwd:
        return jsonify({"error": "Invalid username/email or password."}), 401

    if usr.status != "Active":
        return jsonify({"error": "Account is inactive."}), 403

    token = create_access_token(identity=str(usr.id), additional_claims={"role": usr.role})
    return jsonify({
        "message": f"Logged in as {usr.role}.",
        "access_token": token,
        "user": usr.to_dict(),
    }), 200


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def get_me():
    usr = get_current_user()
    if not usr:
        return jsonify({"error": "User not found."}), 404
    return jsonify({"user": usr.to_dict()}), 200


@auth_bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    usr = get_current_user()
    if not usr:
        return jsonify({"error": "User not found."}), 404

    body = request.get_json() or {}
    if "name" in body and body["name"].strip():
        usr.name = body["name"].strip()
    if "contact_details" in body:
        usr.contact_details = body["contact_details"].strip()
    if "department" in body and body["department"].strip():
        usr.department = body["department"].strip()
    if "roll_number" in body and usr.role == "student":
        usr.roll_number = body["roll_number"].strip().upper()
    if "designation" in body and usr.role == "examiner":
        usr.designation = body["designation"].strip()
    if "specialization" in body and usr.role == "examiner":
        usr.specialization = body["specialization"].strip()
    if "bio" in body:
        usr.bio = body["bio"].strip()
    if "gchat_webhook" in body:
        usr.gchat_webhook = body["gchat_webhook"].strip()

    new_pwd = body.get("new_password")
    if new_pwd:
        if len(new_pwd) < 6:
            return jsonify({"error": "New password must be at least 6 characters."}), 400
        usr.set_password(new_pwd)

    db.session.commit()
    return jsonify({"message": "Profile saved.", "user": usr.to_dict()}), 200


@auth_bp.route("/notifications", methods=["GET"])
@jwt_required()
def list_notifications():
    usr = get_current_user()
    rows = (
        Notification.query.filter_by(user_id=usr.id)
        .order_by(Notification.created_at.desc())
        .limit(40)
        .all()
    )
    unread = Notification.query.filter_by(user_id=usr.id, is_read=False).count()
    return jsonify({
        "notifications": [n.to_dict() for n in rows],
        "unread_count": unread,
    }), 200


@auth_bp.route("/notifications/<int:notif_id>/read", methods=["PUT"])
@jwt_required()
def mark_notification_read(notif_id):
    usr = get_current_user()
    row = Notification.query.filter_by(id=notif_id, user_id=usr.id).first()
    if not row:
        return jsonify({"error": "Notification not found."}), 404
    row.is_read = True
    db.session.commit()
    return jsonify({"message": "Marked read."}), 200


@auth_bp.route("/notifications/read-all", methods=["PUT"])
@jwt_required()
def mark_all_notifications_read():
    usr = get_current_user()
    Notification.query.filter_by(user_id=usr.id, is_read=False).update({"is_read": True})
    db.session.commit()
    return jsonify({"message": "All marked read."}), 200
