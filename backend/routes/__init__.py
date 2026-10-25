from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt
from models import db, User


def role_required(*roles):
    def wrapper_fn(fn):
        @wraps(fn)
        def decorated(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims.get("role") not in roles:
                return jsonify({"error": "Unauthorized for this role."}), 403
            uid = int(get_jwt_identity())
            usr = db.session.get(User, uid)
            if not usr or usr.status != "Active":
                return jsonify({"error": "Account is inactive or missing."}), 403
            return fn(*args, **kwargs)
        return decorated
    return wrapper_fn


def get_current_user():
    verify_jwt_in_request()
    uid = int(get_jwt_identity())
    return db.session.get(User, uid)
