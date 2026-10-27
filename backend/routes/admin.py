from flask import Blueprint, request, jsonify, send_from_directory
from models import (
    db,
    User,
    Course,
    Examination,
    ExaminerAssignment,
    ExaminationRubric,
    ExaminationSlot,
    Booking,
    Evaluation,
    Notification,
    JobExecutionLog,
)
from routes import role_required
from cache import cache_get, cache_set, cache_invalidate_prefix, get_cache_info
from tasks import send_daily_exam_reminders, generate_monthly_exam_report, send_email_safe, dispatch_task
from config import Config

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")


@admin_bp.route("/dashboard", methods=["GET"])
@role_required("admin")
def admin_dashboard():
    cached = cache_get("admin:dashboard")
    if cached:
        cached["cache_info"] = get_cache_info()
        return jsonify(cached), 200

    courses_cnt = Course.query.count()
    exams_cnt = Examination.query.count()
    students_cnt = User.query.filter_by(role="student").count()
    examiners_cnt = User.query.filter_by(role="examiner").count()
    slots_cnt = ExaminationSlot.query.count()
    bookings_cnt = Booking.query.count()
    booked_cnt = Booking.query.filter_by(status="Booked").count()
    completed_cnt = Booking.query.filter_by(status="Completed").count()
    cancelled_cnt = Booking.query.filter_by(status="Cancelled").count()
