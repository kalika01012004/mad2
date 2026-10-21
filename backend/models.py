import json
from datetime import datetime, date, timezone
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


def now_utc():
    return datetime.now(timezone.utc)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, index=True)

    contact_details = db.Column(db.String(100), default="")
    department = db.Column(db.String(100), default="Computer Science")
    roll_number = db.Column(db.String(50), default="")
    designation = db.Column(db.String(100), default="")
    specialization = db.Column(db.String(150), default="")
    bio = db.Column(db.Text, default="")
    gchat_webhook = db.Column(db.String(300), default="")
    status = db.Column(db.String(20), default="Active")
    created_at = db.Column(db.DateTime, default=now_utc)

    def set_password(self, raw_pwd):
        self.password_hash = generate_password_hash(raw_pwd)

    def check_password(self, raw_pwd):
        return check_password_hash(self.password_hash, raw_pwd)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "username": self.username,
            "role": self.role,
            "contact_details": self.contact_details or "",
            "department": self.department or "",
            "roll_number": self.roll_number or "",
            "designation": self.designation or "",
            "specialization": self.specialization or "",
            "bio": self.bio or "",
            "gchat_webhook": self.gchat_webhook or "",
            "status": self.status or "Active",
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Course(db.Model):
    __tablename__ = "courses"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(30), unique=True, nullable=False, index=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, default="")
    department = db.Column(db.String(100), default="Computer Science")
    credits = db.Column(db.Integer, default=4)
