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
        "charts": {
            "popular_examinations": {
                "labels": exam_labels,
                "bookings": exam_bookings,
                "evaluations": exam_evals,
            },
            "examiner_workload": {
                "labels": exm_labels,
                "slots_created": exm_slots,
                "evaluations_completed": exm_evals,
            },
            "booking_trends": {
                "labels": ["Booked", "Completed", "Cancelled"],
                "data": [booked_cnt, completed_cnt, cancelled_cnt],
            },
            "exam_status_distribution": {
                "labels": list(status_map.keys()),
                "data": list(status_map.values()),
            },
        },
        "cache_info": get_cache_info(),
    }
    cache_set("admin:dashboard", data, timeout=60)
    return jsonify(data), 200


@admin_bp.route("/courses", methods=["GET"])
@role_required("admin")
def list_courses():
    rows = Course.query.order_by(Course.code.asc()).all()
    return jsonify({"courses": [c.to_dict() for c in rows]}), 200


@admin_bp.route("/courses", methods=["POST"])
@role_required("admin")
def create_course():
    body = request.get_json() or {}
    code = (body.get("code") or "").strip().upper()
    name = (body.get("name") or "").strip()
    desc = (body.get("description") or "").strip()
    dept = (body.get("department") or "Computer Science").strip()
    credits = int(body.get("credits") or 4)
    sem = (body.get("semester") or "Term 1 - 2026").strip()
    status = (body.get("status") or "Active").strip()

    if not code or not name:
        return jsonify({"error": "Course code and name are required."}), 400

    if Course.query.filter_by(code=code).first():
        return jsonify({"error": f"Course code '{code}' already exists."}), 409

    course = Course(
        code=code,
        name=name,
        description=desc,
        department=dept,
        credits=credits,
        semester=sem,
        status=status,
    )
    db.session.add(course)
    db.session.commit()
    cache_invalidate_prefix("admin:", "exams:", "courses:")
    return jsonify({"message": "Course added.", "course": course.to_dict()}), 201


@admin_bp.route("/courses/<int:course_id>", methods=["PUT"])
@role_required("admin")
def update_course(course_id):
    course = db.session.get(Course, course_id)
    if not course:
        return jsonify({"error": "Course not found."}), 404

    body = request.get_json() or {}
    if "code" in body and body["code"].strip():
        new_code = body["code"].strip().upper()
        dup = Course.query.filter(Course.code == new_code, Course.id != course.id).first()
        if dup:
            return jsonify({"error": f"Course code '{new_code}' is already taken."}), 409
        course.code = new_code
    if "name" in body and body["name"].strip():
        course.name = body["name"].strip()
    if "description" in body:
        course.description = body["description"].strip()
    if "department" in body:
        course.department = body["department"].strip()
    if "credits" in body:
        course.credits = int(body["credits"])
    if "semester" in body:
        course.semester = body["semester"].strip()
    if "status" in body:
        course.status = body["status"].strip()

    db.session.commit()
    cache_invalidate_prefix("admin:", "exams:", "courses:")
    return jsonify({"message": "Course updated.", "course": course.to_dict()}), 200


@admin_bp.route("/courses/<int:course_id>", methods=["DELETE"])
@role_required("admin")
def delete_course(course_id):
    course = db.session.get(Course, course_id)
    if not course:
        return jsonify({"error": "Course not found."}), 404

    db.session.delete(course)
    db.session.commit()
    cache_invalidate_prefix("admin:", "exams:", "courses:")
    return jsonify({"message": "Course removed."}), 200


@admin_bp.route("/examinations", methods=["GET"])
@role_required("admin")
def list_examinations():
    cached = cache_get("exams:admin_list")
    if cached:
        return jsonify({"examinations": cached, "cached": True}), 200

    rows = Examination.query.order_by(Examination.created_at.desc()).all()
    out = [e.to_dict(include_details=True) for e in rows]
    cache_set("exams:admin_list", out, timeout=90)
    return jsonify({"examinations": out, "cached": False}), 200


@admin_bp.route("/examinations", methods=["POST"])
@role_required("admin")
def create_examination():
    body = request.get_json() or {}
    cid = body.get("course_id")
    name = (body.get("name") or "").strip()
    etype = (body.get("exam_type") or "Viva").strip()
    dur = int(body.get("duration") or 30)
    max_m = float(body.get("max_marks") or 100.0)
    pass_m = float(body.get("passing_marks") or 40.0)
    instr = (body.get("instructions") or "").strip()

    sc_start = (body.get("slot_creation_start") or "").strip()
    sc_end = (body.get("slot_creation_end") or "").strip()
    sb_start = (body.get("slot_booking_start") or "").strip()
    sb_end = (body.get("slot_booking_end") or "").strip()
    status = (body.get("status") or "Draft").strip()
    sc_open = bool(body.get("slot_creation_open", status == "Slot Creation"))
    sb_open = bool(body.get("slot_booking_open", status == "Booking Open"))

    if not cid or not name:
        return jsonify({"error": "Course and examination name are required."}), 400
    if not db.session.get(Course, int(cid)):
        return jsonify({"error": "Course not found."}), 404
    if not (sc_start and sc_end and sb_start and sb_end):
        return jsonify({"error": "Slot creation and booking start/end dates are required."}), 400

    exam = Examination(
        course_id=int(cid),
        name=name,
        exam_type=etype,
        duration=dur,
        max_marks=max_m,
        passing_marks=pass_m,
        instructions=instr or "Join 5 minutes before the scheduled start time with valid ID.",
        slot_creation_start=sc_start,
        slot_creation_end=sc_end,
        slot_booking_start=sb_start,
        slot_booking_end=sb_end,
        status=status,
        slot_creation_open=sc_open,
        slot_booking_open=sb_open,
    )
    db.session.add(exam)
    db.session.flush()

    for ex_id in body.get("examiner_ids") or []:
        fac = db.session.get(User, int(ex_id))
        if fac and fac.role == "examiner":
            db.session.add(ExaminerAssignment(examination_id=exam.id, examiner_id=fac.id))

    for r in body.get("rubrics") or []:
        if r.get("criterion_name"):
            db.session.add(
                ExaminationRubric(
                    examination_id=exam.id,
                    criterion_name=r["criterion_name"].strip(),
                    max_marks=float(r.get("max_marks", 25)),
                    weightage=float(r.get("weightage", 25)),
                    description=(r.get("description") or "").strip(),
                )
            )

    db.session.commit()
    cache_invalidate_prefix("admin:", "exams:", "rubrics:", "slots:")
    return jsonify({"message": "Examination created.", "examination": exam.to_dict()}), 201


@admin_bp.route("/examinations/<int:exam_id>", methods=["PUT"])
@role_required("admin")
def update_examination(exam_id):
    exam = db.session.get(Examination, exam_id)
    if not exam:
        return jsonify({"error": "Examination not found."}), 404

    body = request.get_json() or {}
    if "course_id" in body and body["course_id"]:
        exam.course_id = int(body["course_id"])
    if "name" in body and body["name"].strip():
        exam.name = body["name"].strip()
    if "exam_type" in body and body["exam_type"].strip():
        exam.exam_type = body["exam_type"].strip()
    if "duration" in body:
        exam.duration = int(body["duration"])
    if "max_marks" in body:
        exam.max_marks = float(body["max_marks"])
    if "passing_marks" in body:
        exam.passing_marks = float(body["passing_marks"])
    if "instructions" in body:
        exam.instructions = body["instructions"].strip()
    if "slot_creation_start" in body:
        exam.slot_creation_start = body["slot_creation_start"].strip()
    if "slot_creation_end" in body:
        exam.slot_creation_end = body["slot_creation_end"].strip()
    if "slot_booking_start" in body:
        exam.slot_booking_start = body["slot_booking_start"].strip()
    if "slot_booking_end" in body:
        exam.slot_booking_end = body["slot_booking_end"].strip()
    if "status" in body:
        exam.status = body["status"].strip()
    if "slot_creation_open" in body:
        exam.slot_creation_open = bool(body["slot_creation_open"])
    if "slot_booking_open" in body:
        exam.slot_booking_open = bool(body["slot_booking_open"])
    if "results_published" in body:
        exam.results_published = bool(body["results_published"])

    if "examiner_ids" in body and isinstance(body["examiner_ids"], list):
        ExaminerAssignment.query.filter_by(examination_id=exam.id).delete()
        for ex_id in body["examiner_ids"]:
            fac = db.session.get(User, int(ex_id))
            if fac and fac.role == "examiner":
                db.session.add(ExaminerAssignment(examination_id=exam.id, examiner_id=fac.id))

    db.session.commit()
    cache_invalidate_prefix("admin:", "exams:", "rubrics:", "slots:")
    return jsonify({"message": "Examination updated.", "examination": exam.to_dict()}), 200


@admin_bp.route("/examinations/<int:exam_id>", methods=["DELETE"])
@role_required("admin")
def delete_examination(exam_id):
    exam = db.session.get(Examination, exam_id)
    if not exam:
        return jsonify({"error": "Examination not found."}), 404

    db.session.delete(exam)
    db.session.commit()
    cache_invalidate_prefix("admin:", "exams:", "rubrics:", "slots:")
    return jsonify({"message": "Examination deleted."}), 200


@admin_bp.route("/examinations/<int:exam_id>/toggle-slot-creation", methods=["POST"])
@role_required("admin")
def toggle_slot_creation(exam_id):
    exam = db.session.get(Examination, exam_id)
    if not exam:
        return jsonify({"error": "Examination not found."}), 404

    body = request.get_json() or {}
    exam.slot_creation_open = bool(body["open"]) if "open" in body else (not exam.slot_creation_open)

    if exam.slot_creation_open and exam.status == "Draft":
        exam.status = "Slot Creation"
    elif not exam.slot_creation_open and exam.status == "Slot Creation" and not exam.slot_booking_open:
        exam.status = "Draft"

    db.session.commit()
    cache_invalidate_prefix("admin:", "exams:", "slots:")
    label = "opened" if exam.slot_creation_open else "closed"
    return jsonify({
        "message": f"Slot creation {label} for '{exam.name}'.",
        "examination": exam.to_dict(),
    }), 200


@admin_bp.route("/examinations/<int:exam_id>/toggle-slot-booking", methods=["POST"])
@role_required("admin")
def toggle_slot_booking(exam_id):
    exam = db.session.get(Examination, exam_id)
    if not exam:
        return jsonify({"error": "Examination not found."}), 404

    body = request.get_json() or {}
    exam.slot_booking_open = bool(body["open"]) if "open" in body else (not exam.slot_booking_open)

    if exam.slot_booking_open:
        exam.status = "Booking Open"
    elif not exam.slot_booking_open and exam.status == "Booking Open":
        exam.status = "Closed"

    db.session.commit()
    cache_invalidate_prefix("admin:", "exams:", "slots:")
    label = "opened" if exam.slot_booking_open else "closed"
    return jsonify({
        "message": f"Slot booking {label} for '{exam.name}'.",
        "examination": exam.to_dict(),
    }), 200


@admin_bp.route("/examinations/<int:exam_id>/publish-results", methods=["POST"])
@role_required("admin")
def publish_examination_results(exam_id):
    exam = db.session.get(Examination, exam_id)
    if not exam:
        return jsonify({"error": "Examination not found."}), 404

    body = request.get_json() or {}
    publish = bool(body.get("publish", True))
    exam.results_published = publish

    notified = 0
    if publish:
        exam.status = "Completed"
        exam.slot_creation_open = False
        exam.slot_booking_open = False

        evals = Evaluation.query.filter_by(examination_id=exam.id).all()
        for ev in evals:
            ev.status = "Published"
            if ev.student:
                db.session.add(
                    Notification(
                        user_id=ev.student.id,
                        title=f"Results Out: {exam.name}",
                        message=f"Your marks for '{exam.name}': {ev.total_marks} / {exam.max_marks}. Remarks: {ev.remarks or 'Good.'}",
                        notif_type="result",
                        action_url=f"/api/student/bookings/{ev.booking_id}/scorecard",
                    )
                )
                send_email_safe(
                    ev.student.email,
                    f"Result Published: {exam.name}",
                    f"<p>Hello {ev.student.name},</p><p>Your result for <strong>{exam.name}</strong> is published.</p>"
                    f"<p><strong>Marks:</strong> {ev.total_marks} / {exam.max_marks}</p><p><strong>Remarks:</strong> {ev.remarks}</p>",
                )
                notified += 1

    db.session.commit()
    cache_invalidate_prefix("admin:", "exams:", "slots:")
    msg = f"Results published for '{exam.name}' ({notified} notified)." if publish else f"Results unpublished for '{exam.name}'."
    return jsonify({"message": msg, "examination": exam.to_dict()}), 200


@admin_bp.route("/examinations/<int:exam_id>/rubrics", methods=["GET"])
@role_required("admin", "examiner", "student")
def list_exam_rubrics(exam_id):
    key = f"rubrics:exam:{exam_id}"
    cached = cache_get(key)
    if cached is not None:
        return jsonify({"rubrics": cached, "cached": True}), 200

    exam = db.session.get(Examination, exam_id)
    if not exam:
        return jsonify({"error": "Examination not found."}), 404

    rows = [r.to_dict() for r in exam.rubrics]
    cache_set(key, rows, timeout=180)
    return jsonify({"rubrics": rows, "cached": False}), 200


@admin_bp.route("/examinations/<int:exam_id>/rubrics", methods=["POST"])
@role_required("admin")
def create_exam_rubric(exam_id):
    exam = db.session.get(Examination, exam_id)
    if not exam:
        return jsonify({"error": "Examination not found."}), 404

    body = request.get_json() or {}
    cname = (body.get("criterion_name") or "").strip()
    max_m = float(body.get("max_marks") or 0)
    wt = float(body.get("weightage") or 0)
    desc = (body.get("description") or "").strip()

    if not cname or max_m <= 0:
        return jsonify({"error": "Criterion name and positive max marks are required."}), 400

    rubric = ExaminationRubric(
        examination_id=exam.id,
        criterion_name=cname,
        max_marks=max_m,
        weightage=wt,
        description=desc,
    )
    db.session.add(rubric)
    db.session.commit()
    cache_invalidate_prefix(f"rubrics:exam:{exam_id}", "exams:")
    return jsonify({"message": "Rubric added.", "rubric": rubric.to_dict()}), 201


@admin_bp.route("/rubrics/<int:rubric_id>", methods=["PUT"])
@role_required("admin")
def update_exam_rubric(rubric_id):
    rubric = db.session.get(ExaminationRubric, rubric_id)
    if not rubric:
        return jsonify({"error": "Rubric not found."}), 404

    body = request.get_json() or {}
    if "criterion_name" in body and body["criterion_name"].strip():
        rubric.criterion_name = body["criterion_name"].strip()
    if "max_marks" in body:
        rubric.max_marks = float(body["max_marks"])
    if "weightage" in body:
        rubric.weightage = float(body["weightage"])
    if "description" in body:
        rubric.description = body["description"].strip()

    db.session.commit()
    cache_invalidate_prefix(f"rubrics:exam:{rubric.examination_id}", "exams:")
    return jsonify({"message": "Rubric updated.", "rubric": rubric.to_dict()}), 200


@admin_bp.route("/rubrics/<int:rubric_id>", methods=["DELETE"])
@role_required("admin")
def delete_exam_rubric(rubric_id):
    rubric = db.session.get(ExaminationRubric, rubric_id)
    if not rubric:
        return jsonify({"error": "Rubric not found."}), 404

    eid = rubric.examination_id
    db.session.delete(rubric)
    db.session.commit()
    cache_invalidate_prefix(f"rubrics:exam:{eid}", "exams:")
    return jsonify({"message": "Rubric deleted."}), 200


@admin_bp.route("/examiners", methods=["GET"])
@role_required("admin")
def list_examiners():
    rows = User.query.filter_by(role="examiner").order_by(User.name.asc()).all()
    out = []
    for ex in rows:
        item = ex.to_dict()
        item["assigned_exams_count"] = ExaminerAssignment.query.filter_by(examiner_id=ex.id).count()
        item["slots_count"] = ExaminationSlot.query.filter_by(examiner_id=ex.id).count()
        item["evaluations_count"] = Evaluation.query.filter_by(examiner_id=ex.id).count()
        out.append(item)
    return jsonify({"examiners": out}), 200


@admin_bp.route("/examiners", methods=["POST"])
@role_required("admin")
def create_examiner():
    body = request.get_json() or {}
    name = (body.get("name") or "").strip()
    email = (body.get("email") or "").strip().lower()
    uname = (body.get("username") or "").strip().lower() or (email.split("@")[0] if email else "")
    pwd = body.get("password") or "examiner123"
    contact = (body.get("contact_details") or "").strip()
    dept = (body.get("department") or "Computer Science").strip()
    desig = (body.get("designation") or "Assistant Professor").strip()
    spec = (body.get("specialization") or "").strip()
    status = (body.get("status") or "Active").strip()

    if not name or not email:
        return jsonify({"error": "Name and email are required."}), 400
    if len(pwd) < 6:
        return jsonify({"error": "Password must be at least 6 characters."}), 400

    if User.query.filter((User.email == email) | (User.username == uname)).first():
        return jsonify({"error": "User with this email or username already exists."}), 409

    exm = User(
        name=name,
        email=email,
        username=uname,
        role="examiner",
        contact_details=contact,
        department=dept,
        designation=desig,
        specialization=spec,
        status=status,
    )
    exm.set_password(pwd)
    db.session.add(exm)
    db.session.flush()

    for eid in body.get("examination_ids") or []:
        if db.session.get(Examination, int(eid)):
            db.session.add(ExaminerAssignment(examination_id=int(eid), examiner_id=exm.id))

    db.session.commit()
    cache_invalidate_prefix("admin:", "exams:")
    return jsonify({"message": "Examiner added.", "examiner": exm.to_dict()}), 201


@admin_bp.route("/examiners/<int:examiner_id>", methods=["PUT"])
@role_required("admin")
def update_examiner(examiner_id):
    exm = User.query.filter_by(id=examiner_id, role="examiner").first()
    if not exm:
        return jsonify({"error": "Examiner not found."}), 404

    body = request.get_json() or {}
    if "name" in body and body["name"].strip():
        exm.name = body["name"].strip()
    if "contact_details" in body:
        exm.contact_details = body["contact_details"].strip()
    if "department" in body:
        exm.department = body["department"].strip()
    if "designation" in body:
        exm.designation = body["designation"].strip()
    if "specialization" in body:
        exm.specialization = body["specialization"].strip()
    if "status" in body:
        exm.status = body["status"].strip()
    if body.get("password"):
        exm.set_password(body["password"])

    db.session.commit()
    cache_invalidate_prefix("admin:", "exams:")
    return jsonify({"message": "Examiner updated.", "examiner": exm.to_dict()}), 200


@admin_bp.route("/examiners/<int:examiner_id>", methods=["DELETE"])
@role_required("admin")
def delete_examiner(examiner_id):
    exm = User.query.filter_by(id=examiner_id, role="examiner").first()
    if not exm:
        return jsonify({"error": "Examiner not found."}), 404

    db.session.delete(exm)
    db.session.commit()
    cache_invalidate_prefix("admin:", "exams:")
    return jsonify({"message": "Examiner removed."}), 200


@admin_bp.route("/students", methods=["GET"])
@role_required("admin")
def list_students():
    rows = User.query.filter_by(role="student").order_by(User.created_at.desc()).all()
    out = []
    for st in rows:
        item = st.to_dict()
        item["bookings_count"] = Booking.query.filter_by(student_id=st.id).count()
        item["evaluations_count"] = Evaluation.query.filter_by(student_id=st.id).count()
        out.append(item)
    return jsonify({"students": out}), 200


@admin_bp.route("/students/<int:student_id>", methods=["PUT"])
@role_required("admin")
def update_student(student_id):
    st = User.query.filter_by(id=student_id, role="student").first()
    if not st:
        return jsonify({"error": "Student not found."}), 404

    body = request.get_json() or {}
    if "status" in body:
        st.status = body["status"]
    if "department" in body:
        st.department = body["department"]
    if "roll_number" in body:
        st.roll_number = body["roll_number"]
    db.session.commit()
    return jsonify({"message": "Student updated.", "student": st.to_dict()}), 200


@admin_bp.route("/slots", methods=["GET"])
@role_required("admin")
def list_all_slots():
    eid = request.args.get("examination_id", type=int)
    exm_id = request.args.get("examiner_id", type=int)

    q = ExaminationSlot.query
    if eid:
        q = q.filter_by(examination_id=eid)
    if exm_id:
        q = q.filter_by(examiner_id=exm_id)

    rows = q.order_by(ExaminationSlot.date.asc(), ExaminationSlot.start_time.asc()).all()
    return jsonify({"slots": [s.to_dict(include_bookings=True) for s in rows]}), 200


@admin_bp.route("/slots/<int:slot_id>/reschedule", methods=["PUT"])
@role_required("admin")
def admin_reschedule_slot(slot_id):
    slot = db.session.get(ExaminationSlot, slot_id)
    if not slot:
        return jsonify({"error": "Slot not found."}), 404

    body = request.get_json() or {}
    prev_slot_str = f"{slot.date} ({slot.start_time}-{slot.end_time})"

    if "date" in body and body["date"].strip():
        slot.date = body["date"].strip()
    if "start_time" in body and body["start_time"].strip():
        slot.start_time = body["start_time"].strip()
    if "end_time" in body and body["end_time"].strip():
        slot.end_time = body["end_time"].strip()
    if "meeting_link" in body:
        slot.meeting_link = body["meeting_link"].strip()
    if "venue" in body:
        slot.venue = body["venue"].strip()
    if "max_capacity" in body:
        slot.max_capacity = int(body["max_capacity"])
        slot.recalculate_seats()
    if "status" in body:
        slot.status = body["status"].strip()

    if "examiner_id" in body and body["examiner_id"]:
        new_ex = User.query.filter_by(id=int(body["examiner_id"]), role="examiner").first()
        if not new_ex:
            return jsonify({"error": "Examiner not found."}), 404
        slot.examiner_id = new_ex.id
        if not ExaminerAssignment.query.filter_by(examination_id=slot.examination_id, examiner_id=new_ex.id).first():
            db.session.add(ExaminerAssignment(examination_id=slot.examination_id, examiner_id=new_ex.id))

    for bk in slot.bookings:
        if bk.status == "Booked":
            bk.rescheduled_by_admin = True
            bk.admin_notes = body.get("reason") or f"Updated from {prev_slot_str} to {slot.date} ({slot.start_time}-{slot.end_time})."
            db.session.add(
                Notification(
                    user_id=bk.student_id,
                    title="Examination Slot Updated",
                    message=(
                        f"Your slot for '{slot.examination.name}' is now on {slot.date} "
                        f"({slot.start_time}-{slot.end_time}) with {slot.examiner.name if slot.examiner else ''}."
                    ),
                    notif_type="booking",
