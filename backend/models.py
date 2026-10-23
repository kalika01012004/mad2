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
            {
                "id": a.examiner.id,
                "name": a.examiner.name,
                "email": a.examiner.email,
                "department": a.examiner.department,
            }
            for a in self.assignments
            if a.examiner
        ]
        res = {
            "id": self.id,
            "course_id": self.course_id,
            "course_code": self.course.code if self.course else "",
            "course_name": self.course.name if self.course else "",
            "name": self.name,
            "exam_type": self.exam_type,
            "duration": self.duration,
            "max_marks": self.max_marks,
            "passing_marks": self.passing_marks,
            "instructions": self.instructions or "",
            "slot_creation_start": self.slot_creation_start,
            "slot_creation_end": self.slot_creation_end,
            "slot_booking_start": self.slot_booking_start,
            "slot_booking_end": self.slot_booking_end,
            "status": self.status,
            "slot_creation_open": self.slot_creation_open,
            "slot_booking_open": self.slot_booking_open,
            "results_published": self.results_published,
            "can_create_slots": self.is_slot_creation_allowed(),
            "can_book_slots": self.is_slot_booking_allowed(),
            "assigned_examiners": faculty,
            "assigned_examiner_ids": [f["id"] for f in faculty],
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
        if include_details:
            res["rubrics"] = [r.to_dict() for r in self.rubrics]
            res["slots_count"] = len(self.slots)
            res["available_slots_count"] = sum(
                1 for s in self.slots if s.status == "Available" and s.available_seats > 0
            )
        return res


class ExaminationRubric(db.Model):
    __tablename__ = "examination_rubrics"

    id = db.Column(db.Integer, primary_key=True)
    examination_id = db.Column(db.Integer, db.ForeignKey("examinations.id", ondelete="CASCADE"), nullable=False)
    criterion_name = db.Column(db.String(120), nullable=False)
    max_marks = db.Column(db.Float, nullable=False)
    weightage = db.Column(db.Float, nullable=False, default=25.0)
    description = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=now_utc)

    def to_dict(self):
        return {
            "id": self.id,
            "examination_id": self.examination_id,
            "criterion_name": self.criterion_name,
            "max_marks": self.max_marks,
            "weightage": self.weightage,
            "description": self.description or "",
        }


class ExaminationSlot(db.Model):
    __tablename__ = "examination_slots"

    id = db.Column(db.Integer, primary_key=True)
    examination_id = db.Column(db.Integer, db.ForeignKey("examinations.id", ondelete="CASCADE"), nullable=False)
    examiner_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    date = db.Column(db.String(20), nullable=False, index=True)
    start_time = db.Column(db.String(10), nullable=False)
    end_time = db.Column(db.String(10), nullable=False)
    max_capacity = db.Column(db.Integer, nullable=False, default=1)
    available_seats = db.Column(db.Integer, nullable=False, default=1)
    status = db.Column(db.String(20), nullable=False, default="Available")
    meeting_link = db.Column(db.String(255), default="")
    venue = db.Column(db.String(120), default="Online / Google Meet")
    created_at = db.Column(db.DateTime, default=now_utc)

    examiner = db.relationship("User", foreign_keys=[examiner_id])
    bookings = db.relationship("Booking", backref="slot", lazy=True, cascade="all, delete-orphan")

    def recalculate_seats(self):
        used = Booking.query.filter(
            Booking.slot_id == self.id,
            Booking.status.in_(["Booked", "Completed"]),
        ).count()
        self.available_seats = max(0, self.max_capacity - used)
        if self.status not in ("Cancelled", "Completed"):
            self.status = "Full" if self.available_seats <= 0 else "Available"

    def to_dict(self, include_bookings=False):
        booked_cnt = Booking.query.filter(
            Booking.slot_id == self.id,
            Booking.status != "Cancelled",
        ).count()
        res = {
            "id": self.id,
            "examination_id": self.examination_id,
            "examination_name": self.examination.name if self.examination else "",
            "course_code": self.examination.course.code if (self.examination and self.examination.course) else "",
            "course_name": self.examination.course.name if (self.examination and self.examination.course) else "",
            "exam_type": self.examination.exam_type if self.examination else "",
            "examiner_id": self.examiner_id,
            "examiner_name": self.examiner.name if self.examiner else "",
            "examiner_email": self.examiner.email if self.examiner else "",
            "examiner_department": self.examiner.department if self.examiner else "",
            "date": self.date,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "max_capacity": self.max_capacity,
            "available_seats": self.available_seats,
            "booked_count": booked_cnt,
            "status": self.status,
            "meeting_link": self.meeting_link or "",
            "venue": self.venue or "Online",
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
        if include_bookings:
            res["bookings"] = [b.to_dict() for b in self.bookings]
        return res


class Booking(db.Model):
    __tablename__ = "bookings"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    slot_id = db.Column(db.Integer, db.ForeignKey("examination_slots.id", ondelete="CASCADE"), nullable=False, index=True)
    examination_id = db.Column(db.Integer, db.ForeignKey("examinations.id", ondelete="CASCADE"), nullable=False, index=True)
    booking_date = db.Column(db.DateTime, default=now_utc)
    status = db.Column(db.String(20), nullable=False, default="Booked")
    rescheduled_by_admin = db.Column(db.Boolean, default=False)
    admin_notes = db.Column(db.Text, default="")

    student = db.relationship("User", foreign_keys=[student_id])
    examination = db.relationship("Examination", foreign_keys=[examination_id])
    evaluation = db.relationship("Evaluation", backref="booking", uselist=False, cascade="all, delete-orphan")

    def to_dict(self):
        exam = self.examination or (self.slot.examination if self.slot else None)
        published = exam.results_published if exam else False
        return {
            "id": self.id,
            "student_id": self.student_id,
            "student_name": self.student.name if self.student else "",
            "student_email": self.student.email if self.student else "",
            "student_roll_number": self.student.roll_number if self.student else "",
            "student_department": self.student.department if self.student else "",
            "slot_id": self.slot_id,
            "examination_id": self.examination_id,
            "examination_name": exam.name if exam else "",
            "exam_type": exam.exam_type if exam else "",
            "max_marks": exam.max_marks if exam else 100.0,
            "passing_marks": exam.passing_marks if exam else 40.0,
            "course_code": exam.course.code if (exam and exam.course) else "",
            "course_name": exam.course.name if (exam and exam.course) else "",
            "slot_date": self.slot.date if self.slot else "",
            "start_time": self.slot.start_time if self.slot else "",
            "end_time": self.slot.end_time if self.slot else "",
            "meeting_link": self.slot.meeting_link if self.slot else "",
            "venue": self.slot.venue if self.slot else "",
            "examiner_id": self.slot.examiner_id if self.slot else None,
            "examiner_name": self.slot.examiner.name if (self.slot and self.slot.examiner) else "",
            "booking_date": self.booking_date.isoformat() if self.booking_date else None,
            "status": self.status,
            "rescheduled_by_admin": self.rescheduled_by_admin,
            "admin_notes": self.admin_notes or "",
            "results_published": published,
            "slot_booking_end": exam.slot_booking_end if exam else "",
            "can_book_slots": exam.is_slot_booking_allowed() if exam else False,
            "evaluation": self.evaluation.to_dict() if self.evaluation else None,
        }


class Evaluation(db.Model):
    __tablename__ = "evaluations"

    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey("bookings.id", ondelete="CASCADE"), unique=True, nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    examiner_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    examination_id = db.Column(db.Integer, db.ForeignKey("examinations.id", ondelete="CASCADE"), nullable=False, index=True)
    total_marks = db.Column(db.Float, nullable=False, default=0.0)
    remarks = db.Column(db.Text, default="")
    rubric_breakdown = db.Column(db.Text, default="[]")
    evaluation_date = db.Column(db.DateTime, default=now_utc)
    status = db.Column(db.String(20), nullable=False, default="Submitted")

    student = db.relationship("User", foreign_keys=[student_id])
    examiner = db.relationship("User", foreign_keys=[examiner_id])
    examination = db.relationship("Examination", foreign_keys=[examination_id])

    def get_breakdown(self):
        try:
