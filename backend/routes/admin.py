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
    evals_cnt = Evaluation.query.count()

    exams = Examination.query.all()
    exam_labels = []
    exam_bookings = []
    exam_evals = []
    for ex in exams:
        exam_labels.append(ex.name)
        b_total = Booking.query.filter(Booking.examination_id == ex.id, Booking.status != "Cancelled").count()
        e_total = Evaluation.query.filter_by(examination_id=ex.id).count()
        exam_bookings.append(b_total)
        exam_evals.append(e_total)

    examiners = User.query.filter_by(role="examiner").all()
    exm_labels = []
    exm_slots = []
    exm_evals = []
    for exm in examiners:
        exm_labels.append(exm.name)
        exm_slots.append(ExaminationSlot.query.filter_by(examiner_id=exm.id).count())
        exm_evals.append(Evaluation.query.filter_by(examiner_id=exm.id).count())

    status_map = {}
    for st in ["Draft", "Slot Creation", "Booking Open", "Closed", "Completed"]:
        status_map[st] = Examination.query.filter_by(status=st).count()

    data = {
        "summary": {
            "total_courses": courses_cnt,
            "total_examinations": exams_cnt,
            "total_students": students_cnt,
            "total_examiners": examiners_cnt,
            "total_slots": slots_cnt,
            "total_bookings": bookings_cnt,
            "active_bookings": booked_cnt,
            "completed_bookings": completed_cnt,
            "cancelled_bookings": cancelled_cnt,
            "total_evaluations": evals_cnt,
        },
