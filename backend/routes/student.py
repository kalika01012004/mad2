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
        return jsonify({"examinations": cached, "cached": True}), 200

    qry = Examination.query.filter(Examination.status != "Draft")
    if cid:
        qry = qry.filter_by(course_id=cid)
    if etype:
        qry = qry.filter_by(exam_type=etype)
    if st:
        qry = qry.filter_by(status=st)

    rows = qry.order_by(Examination.created_at.desc()).all()
    out = []
    for ex in rows:
        if q:
            cmatch = ex.course and (q in ex.course.code.lower() or q in ex.course.name.lower())
            if not (q in ex.name.lower() or q in ex.exam_type.lower() or cmatch):
                continue
        out.append(ex.to_dict(include_details=True))

    cache_set(key, out, timeout=90)
    return jsonify({"examinations": out, "cached": False}), 200


@student_bp.route("/examinations/<int:exam_id>/slots", methods=["GET"])
@role_required("student")
def list_examination_slots_for_student(exam_id):
    key = f"slots:exam:{exam_id}"
    cached = cache_get(key)
    if cached is not None:
        return jsonify({"slots": cached, "cached": True}), 200

    exam = db.session.get(Examination, exam_id)
    if not exam or exam.status == "Draft":
        return jsonify({"error": "Examination not found."}), 404

    rows = (
        ExaminationSlot.query.filter_by(examination_id=exam.id)
        .filter(ExaminationSlot.status != "Cancelled")
        .order_by(ExaminationSlot.date.asc(), ExaminationSlot.start_time.asc())
        .all()
    )
    out = [s.to_dict(include_bookings=False) for s in rows]
    cache_set(key, out, timeout=60)
    return jsonify({"slots": out, "cached": False}), 200


@student_bp.route("/bookings", methods=["GET"])
@role_required("student")
def list_my_bookings():
    usr = get_current_user()
    rows = Booking.query.filter_by(student_id=usr.id).order_by(Booking.booking_date.desc()).all()
    return jsonify({"bookings": [b.to_dict() for b in rows]}), 200


@student_bp.route("/bookings", methods=["POST"])
@role_required("student")
def book_slot():
    usr = get_current_user()
    body = request.get_json() or {}
    sid = body.get("slot_id")
    if not sid:
        return jsonify({"error": "slot_id is required."}), 400

    slot = db.session.get(ExaminationSlot, int(sid))
    if not slot:
        return jsonify({"error": "Slot not found."}), 404

    exam = slot.examination
    if not exam:
        return jsonify({"error": "Examination not found."}), 404

    if not exam.is_slot_booking_allowed():
        return jsonify({
            "error": f"Booking is closed for '{exam.name}' ({exam.slot_booking_start} to {exam.slot_booking_end})."
        }), 400

    existing = Booking.query.filter(
        Booking.student_id == usr.id,
        Booking.examination_id == exam.id,
        Booking.status.in_(["Booked", "Completed"]),
    ).first()
    if existing:
        return jsonify({
            "error": f"You already have a booking for '{exam.name}'. Only one slot is allowed per examination."
        }), 409

    slot.recalculate_seats()
    if slot.status != "Available" or slot.available_seats <= 0:
        return jsonify({"error": "This slot is full or unavailable."}), 400
