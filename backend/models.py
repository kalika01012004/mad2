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
