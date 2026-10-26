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

