import os
from datetime import date
from flask import Blueprint, request, jsonify, send_from_directory, send_file
from models import (
    db,
    Course,
    Examination,
    ExaminationSlot,
    Booking,
    Notification,
)
from routes import role_required, get_current_user
from cache import cache_get, cache_set, cache_invalidate_prefix
from tasks import export_student_exam_history_csv, generate_student_scorecard_pdf, dispatch_task
from config import Config

student_bp = Blueprint("student", __name__, url_prefix="/api/student")


@student_bp.route("/dashboard", methods=["GET"])
@role_required("student")
def student_dashboard():
    usr = get_current_user()

    exams_list = cache_get("exams:student_available")
    if exams_list is None:
        rows = (
            Examination.query.filter(Examination.status != "Draft")
            .order_by(Examination.created_at.desc())
            .all()
