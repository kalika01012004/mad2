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
    cap = int(body.get("max_capacity") or 1)
    link = (body.get("meeting_link") or "").strip()
    venue = (body.get("venue") or "Online / Google Meet").strip()

    if not eid or not s_date or not start_t or not end_t:
        return jsonify({"error": "Examination, date, start time, and end time are required."}), 400
    if cap < 1:
        return jsonify({"error": "Capacity must be at least 1."}), 400
    if start_t >= end_t:
        return jsonify({"error": "End time must be after start time."}), 400

    exam = db.session.get(Examination, int(eid))
    if not exam:
        return jsonify({"error": "Examination not found."}), 404

    if not ExaminerAssignment.query.filter_by(examination_id=exam.id, examiner_id=usr.id).first():
        return jsonify({"error": "You are not assigned to this examination."}), 403

    if not exam.is_slot_creation_allowed():
        return jsonify({
            "error": f"Slot creation is closed for '{exam.name}' ({exam.slot_creation_start} to {exam.slot_creation_end})."
        }), 400

    same_day = ExaminationSlot.query.filter_by(examiner_id=usr.id, date=s_date).all()
    for es in same_day:
        if es.status != "Cancelled":
            if not (end_t <= es.start_time or start_t >= es.end_time):
                return jsonify({
                    "error": f"Overlaps with your existing slot ({es.start_time} - {es.end_time}) on {s_date}."
                }), 409

    slot = ExaminationSlot(
        examination_id=exam.id,
        examiner_id=usr.id,
        date=s_date,
        start_time=start_t,
        end_time=end_t,
        max_capacity=cap,
        available_seats=cap,
        status="Available",
        meeting_link=link,
        venue=venue,
    )
    db.session.add(slot)
    db.session.commit()
    cache_invalidate_prefix("admin:", "exams:", "slots:")
    return jsonify({"message": "Slot created.", "slot": slot.to_dict()}), 201


@examiner_bp.route("/slots/<int:slot_id>", methods=["PUT"])
@role_required("examiner")
def update_slot(slot_id):
    usr = get_current_user()
    slot = ExaminationSlot.query.filter_by(id=slot_id, examiner_id=usr.id).first()
    if not slot:
        return jsonify({"error": "Slot not found."}), 404

    exam = slot.examination
    body = request.get_json() or {}

    schedule_edit = any(k in body for k in ("date", "start_time", "end_time", "max_capacity"))
    active_bk = [b for b in slot.bookings if b.status != "Cancelled"]

    if schedule_edit and (exam.has_booking_started() or len(active_bk) > 0):
        return jsonify({
            "error": "Cannot modify slot timing or capacity after booking starts or once students have booked."
        }), 400

    if "date" in body and body["date"].strip():
        slot.date = body["date"].strip()
    if "start_time" in body and body["start_time"].strip():
        slot.start_time = body["start_time"].strip()
    if "end_time" in body and body["end_time"].strip():
        slot.end_time = body["end_time"].strip()
    if slot.start_time >= slot.end_time:
        return jsonify({"error": "End time must be after start time."}), 400

    if "max_capacity" in body:
        new_cap = int(body["max_capacity"])
        if new_cap < len(active_bk) or new_cap < 1:
            return jsonify({"error": "Invalid capacity."}), 400
        slot.max_capacity = new_cap
        slot.recalculate_seats()

    if "meeting_link" in body:
        slot.meeting_link = body["meeting_link"].strip()
    if "venue" in body:
        slot.venue = body["venue"].strip()
    if "status" in body and body["status"] in ("Available", "Completed", "Cancelled"):
        slot.status = body["status"]

    db.session.commit()
    cache_invalidate_prefix("admin:", "exams:", "slots:")
    return jsonify({"message": "Slot updated.", "slot": slot.to_dict(include_bookings=True)}), 200


@examiner_bp.route("/slots/<int:slot_id>", methods=["DELETE"])
@role_required("examiner")
def delete_slot(slot_id):
    usr = get_current_user()
    slot = ExaminationSlot.query.filter_by(id=slot_id, examiner_id=usr.id).first()
    if not slot:
        return jsonify({"error": "Slot not found."}), 404

    exam = slot.examination
    active_bk = [b for b in slot.bookings if b.status != "Cancelled"]
    if exam.has_booking_started() or len(active_bk) > 0:
        return jsonify({
            "error": "Cannot remove slot after booking has started or when students are booked."
        }), 400

    db.session.delete(slot)
    db.session.commit()
    cache_invalidate_prefix("admin:", "exams:", "slots:")
    return jsonify({"message": "Slot deleted."}), 200


@examiner_bp.route("/bookings/<int:booking_id>/evaluate", methods=["POST"])
@role_required("examiner")
def evaluate_student(booking_id):
    usr = get_current_user()
    bk = db.session.get(Booking, booking_id)
    if not bk:
        return jsonify({"error": "Booking not found."}), 404

    if not bk.slot or bk.slot.examiner_id != usr.id:
        return jsonify({"error": "You can only evaluate students booked in your own slots."}), 403

    if bk.status == "Cancelled":
        return jsonify({"error": "Cannot evaluate a cancelled booking."}), 400

    exam = bk.examination
    body = request.get_json() or {}
    remarks = (body.get("remarks") or "").strip()
    scores = body.get("rubric_scores") or []

    rubric_map = {r.id: r for r in exam.rubrics}
    breakdown = []
    total = 0.0

    if scores and rubric_map:
        for item in scores:
            rid = int(item.get("rubric_id", 0))
            robj = rubric_map.get(rid)
            if not robj:
                continue
            pts = float(item.get("marks_awarded", 0))
            if pts < 0 or pts > robj.max_marks:
                return jsonify({
                    "error": f"Marks for '{robj.criterion_name}' must be between 0 and {robj.max_marks}."
                }), 400
            total += pts
            breakdown.append({
                "rubric_id": robj.id,
                "criterion_name": robj.criterion_name,
                "max_marks": robj.max_marks,
                "weightage": robj.weightage,
                "marks_awarded": pts,
                "comment": (item.get("comment") or "").strip(),
            })
    else:
        if "total_marks" not in body:
            return jsonify({"error": "Provide rubric_scores or total_marks."}), 400
        total = float(body["total_marks"])

    if total < 0 or total > exam.max_marks:
        return jsonify({"error": f"Total marks ({total}) cannot exceed {exam.max_marks}."}), 400

    ev = bk.evaluation
    if not ev:
        ev = Evaluation(
            booking_id=bk.id,
            student_id=bk.student_id,
            examiner_id=usr.id,
            examination_id=exam.id,
        )
        db.session.add(ev)

    ev.total_marks = round(total, 2)
    ev.remarks = remarks
    ev.rubric_breakdown = json.dumps(breakdown)
    ev.evaluation_date = datetime.now(timezone.utc)
    ev.status = "Published" if exam.results_published else "Submitted"

    bk.status = "Completed"

