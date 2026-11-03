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
        )
        exams_list = [e.to_dict(include_details=True) for e in rows]
        cache_set("exams:student_available", exams_list, timeout=90)

    slots_list = cache_get("slots:student_available")
    if slots_list is None:
        open_rows = (
            ExaminationSlot.query.filter(
                ExaminationSlot.status == "Available",
                ExaminationSlot.available_seats > 0,
            )
            .order_by(ExaminationSlot.date.asc(), ExaminationSlot.start_time.asc())
            .all()
        )
        slots_list = [s.to_dict() for s in open_rows if s.examination and s.examination.status != "Draft"]
        cache_set("slots:student_available", slots_list, timeout=60)

    my_bk = (
        Booking.query.filter_by(student_id=usr.id)
        .order_by(Booking.booking_date.desc())
        .all()
    )
    bk_dicts = [b.to_dict() for b in my_bk]

    today_str = date.today().isoformat()
    upcoming = [b for b in bk_dicts if b["status"] == "Booked" and b["slot_date"] >= today_str]
    booked_exam_ids = [b["examination_id"] for b in bk_dicts if b["status"] in ("Booked", "Completed")]
    published = [b for b in bk_dicts if b["evaluation"] and b["results_published"]]
    courses = Course.query.filter_by(status="Active").order_by(Course.code.asc()).all()

    return jsonify({
        "summary": {
            "available_examinations_count": len(exams_list),
            "available_slots_count": len(slots_list),
            "upcoming_examinations_count": len(upcoming),
            "total_bookings_count": len(bk_dicts),
            "published_results_count": len(published),
        },
        "courses": [c.to_dict() for c in courses],
        "available_examinations": exams_list,
        "available_slots": slots_list,
        "upcoming_examinations": upcoming,
        "bookings": bk_dicts,
        "active_booked_exam_ids": booked_exam_ids,
        "published_results": published,
    }), 200


@student_bp.route("/examinations", methods=["GET"])
@role_required("student")
def search_examinations():
    q = (request.args.get("q") or "").strip().lower()
    cid = request.args.get("course_id", type=int)
    etype = (request.args.get("exam_type") or "").strip()
    st = (request.args.get("status") or "").strip()

    key = f"exams:search:{q}:{cid}:{etype}:{st}"
    cached = cache_get(key)
    if cached is not None:
