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
    semester = db.Column(db.String(40), default="Term 1 - 2026")
    status = db.Column(db.String(20), default="Active")
    created_at = db.Column(db.DateTime, default=now_utc)

    examinations = db.relationship("Examination", backref="course", lazy=True, cascade="all, delete-orphan")

    def to_dict(self, include_counts=True):
        res = {
            "id": self.id,
            "code": self.code,
            "name": self.name,
            "description": self.description or "",
            "department": self.department or "",
            "credits": self.credits,
            "semester": self.semester or "",
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
        if include_counts:
            res["examinations_count"] = len(self.examinations)
        return res


class ExaminerAssignment(db.Model):
    __tablename__ = "examiner_assignments"

    id = db.Column(db.Integer, primary_key=True)
    examination_id = db.Column(db.Integer, db.ForeignKey("examinations.id", ondelete="CASCADE"), nullable=False)
    examiner_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    assigned_at = db.Column(db.DateTime, default=now_utc)

    examiner = db.relationship("User", foreign_keys=[examiner_id])

    __table_args__ = (
        db.UniqueConstraint("examination_id", "examiner_id", name="uq_exam_examiner"),
    )


class Examination(db.Model):
    __tablename__ = "examinations"

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    name = db.Column(db.String(160), nullable=False)
    exam_type = db.Column(db.String(50), nullable=False, default="Viva")
    duration = db.Column(db.Integer, nullable=False, default=30)
    max_marks = db.Column(db.Float, nullable=False, default=100.0)
    passing_marks = db.Column(db.Float, nullable=False, default=40.0)
    instructions = db.Column(db.Text, default="Join 5 minutes before your scheduled slot with your student ID.")

    slot_creation_start = db.Column(db.String(25), nullable=False)
    slot_creation_end = db.Column(db.String(25), nullable=False)
    slot_booking_start = db.Column(db.String(25), nullable=False)
    slot_booking_end = db.Column(db.String(25), nullable=False)

    status = db.Column(db.String(30), nullable=False, default="Draft")
    slot_creation_open = db.Column(db.Boolean, default=False)
    slot_booking_open = db.Column(db.Boolean, default=False)
    results_published = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=now_utc)

    rubrics = db.relationship("ExaminationRubric", backref="examination", lazy=True, cascade="all, delete-orphan")
    slots = db.relationship("ExaminationSlot", backref="examination", lazy=True, cascade="all, delete-orphan")
    assignments = db.relationship("ExaminerAssignment", backref="examination", lazy=True, cascade="all, delete-orphan")

    def is_slot_creation_allowed(self):
        if self.status in ("Closed", "Completed"):
            return False
        if self.slot_creation_open or self.status == "Slot Creation":
            today = date.today().isoformat()
            if self.slot_creation_start and self.slot_creation_end:
                if self.slot_creation_start <= today <= self.slot_creation_end:
                    return True
            if self.slot_creation_open:
                return True
        return False

    def is_slot_booking_allowed(self):
        if self.status in ("Closed", "Completed", "Draft"):
            return False
        if self.slot_booking_open or self.status == "Booking Open":
            today = date.today().isoformat()
            if self.slot_booking_start and self.slot_booking_end:
                if self.slot_booking_start <= today <= self.slot_booking_end:
                    return True
            if self.slot_booking_open:
                return True
        return False

    def has_booking_started(self):
        if self.slot_booking_open or self.status in ("Booking Open", "Closed", "Completed"):
            return True
        today = date.today().isoformat()
        if self.slot_booking_start and today >= self.slot_booking_start and self.status == "Booking Open":
            return True
        return False

    def to_dict(self, include_details=True):
        faculty = [
