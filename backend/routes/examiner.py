import json
from datetime import datetime, timezone
from flask import Blueprint, request, jsonify
from models import (
    db,
    Examination,
    ExaminerAssignment,
    ExaminationSlot,
    Booking,
    Evaluation,
)
from routes import role_required, get_current_user
from cache import cache_invalidate_prefix

examiner_bp = Blueprint("examiner", __name__, url_prefix="/api/examiner")


@examiner_bp.route("/dashboard", methods=["GET"])
@role_required("examiner")
def examiner_dashboard():
    usr = get_current_user()

    assigned = ExaminerAssignment.query.filter_by(examiner_id=usr.id).all()
    exam_ids = {a.examination_id for a in assigned}

    slots = (
        ExaminationSlot.query.filter_by(examiner_id=usr.id)
        .order_by(ExaminationSlot.date.asc(), ExaminationSlot.start_time.asc())
        .all()
    )
    for s in slots:
        exam_ids.add(s.examination_id)

    exams = Examination.query.filter(Examination.id.in_(exam_ids)).all() if exam_ids else []
    slot_ids = [s.id for s in slots]

    bookings = (
        Booking.query.filter(Booking.slot_id.in_(slot_ids), Booking.status != "Cancelled")
        .order_by(Booking.booking_date.desc())
        .all()
        if slot_ids
        else []
    )

    pending = sum(1 for b in bookings if not b.evaluation)
    done = sum(1 for b in bookings if b.evaluation)

    return jsonify({
        "summary": {
            "assigned_examinations_count": len(exams),
            "created_slots_count": len(slots),
            "booked_students_count": len(bookings),
            "pending_evaluations_count": pending,
            "completed_evaluations_count": done,
        },
        "assigned_examinations": [e.to_dict(include_details=True) for e in exams],
        "slots": [s.to_dict(include_bookings=True) for s in slots],
        "bookings": [b.to_dict() for b in bookings],
    }), 200


@examiner_bp.route("/examinations", methods=["GET"])
@role_required("examiner")
def list_assigned_examinations():
    usr = get_current_user()
    assigned = ExaminerAssignment.query.filter_by(examiner_id=usr.id).all()
    ids = [a.examination_id for a in assigned]
    exams = Examination.query.filter(Examination.id.in_(ids)).all() if ids else []
    return jsonify({"examinations": [e.to_dict(include_details=True) for e in exams]}), 200


@examiner_bp.route("/slots", methods=["GET"])
@role_required("examiner")
def list_my_slots():
    usr = get_current_user()
    eid = request.args.get("examination_id", type=int)
    q = ExaminationSlot.query.filter_by(examiner_id=usr.id)
    if eid:
        q = q.filter_by(examination_id=eid)
    rows = q.order_by(ExaminationSlot.date.asc(), ExaminationSlot.start_time.asc()).all()
    return jsonify({"slots": [s.to_dict(include_bookings=True) for s in rows]}), 200


@examiner_bp.route("/slots", methods=["POST"])
@role_required("examiner")
def create_slot():
    usr = get_current_user()
    body = request.get_json() or {}

    eid = body.get("examination_id")
    s_date = (body.get("date") or "").strip()
    start_t = (body.get("start_time") or "").strip()
    end_t = (body.get("end_time") or "").strip()
