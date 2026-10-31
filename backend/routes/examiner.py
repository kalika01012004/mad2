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
