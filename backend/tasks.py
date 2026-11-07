import os
import csv
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from datetime import datetime, date, timezone
import requests

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

from celery_app import celery_app
from config import Config
from models import db, User, Examination, ExaminationSlot, Booking, Evaluation, Notification, JobExecutionLog


def send_email_safe(to_email, subject, html_body, attachment_path=None):
    try:
        msg = MIMEMultipart()
        msg["From"] = Config.SMTP_SENDER
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(html_body, "html"))

        if attachment_path and os.path.exists(attachment_path):
            with open(attachment_path, "rb") as fp:
                part = MIMEApplication(fp.read(), Name=os.path.basename(attachment_path))
            part["Content-Disposition"] = f'attachment; filename="{os.path.basename(attachment_path)}"'
            msg.attach(part)

        with smtplib.SMTP(Config.SMTP_HOST, Config.SMTP_PORT, timeout=2) as srv:
            srv.send_message(msg)
        return True
    except Exception:
        return False


def send_gchat_webhook_safe(webhook_url, text_message):
    url = webhook_url or Config.GCHAT_WEBHOOK_URL
    if not url:
        return False
    try:
        resp = requests.post(url, json={"text": text_message}, timeout=3)
        return resp.status_code < 400
    except Exception:
        return False


@celery_app.task(name="tasks.send_daily_exam_reminders")
def send_daily_exam_reminders(triggered_by="celery-beat"):
    today_str = date.today().isoformat()
    bookings = Booking.query.filter_by(status="Booked").all()

    count = 0
    cards = []

    for b in bookings:
        slot = b.slot
        exam = b.examination
        student = b.student
        if not slot or not exam or not student:
            continue

        if slot.date >= today_str:
            examiner_name = slot.examiner.name if slot.examiner else "Assigned Faculty"
            instr = exam.instructions or "Join 5 minutes before the scheduled start time with valid ID."
            chat_msg = (
                f"Daily Examination Reminder\n"
                f"Student: {student.name} ({student.roll_number or student.email})\n"
                f"Examination: {exam.name} ({exam.course.code if exam.course else ''})\n"
                f"Date & Time: {slot.date} | {slot.start_time} - {slot.end_time}\n"
                f"Examiner: {examiner_name}\n"
                f"Venue: {slot.venue or 'Online'} {slot.meeting_link or ''}\n"
                f"Instructions: {instr}"
            )
            send_gchat_webhook_safe(student.gchat_webhook, chat_msg)

            mail_html = f"""
            <div style="font-family: sans-serif; border: 1px solid #dee2e6; border-radius: 6px; padding: 14px; margin-bottom: 10px;">
                <h4 style="color: #0d6efd; margin-top: 0;">Upcoming Examination Reminder</h4>
                <p>Hello <strong>{student.name}</strong>,</p>
                <p>Here are the details for your upcoming examination slot:</p>
                <ul>
                    <li><strong>Examination:</strong> {exam.name} ({exam.exam_type})</li>
                    <li><strong>Course:</strong> {exam.course.code if exam.course else ''} - {exam.course.name if exam.course else ''}</li>
                    <li><strong>Date &amp; Time:</strong> {slot.date} ({slot.start_time} to {slot.end_time})</li>
                    <li><strong>Assigned Examiner:</strong> {examiner_name}</li>
                    <li><strong>Venue:</strong> {slot.venue} {(' - ' + slot.meeting_link) if slot.meeting_link else ''}</li>
                    <li><strong>Instructions:</strong> {instr}</li>
                </ul>
            </div>
            """
            send_email_safe(student.email, f"Examination Reminder: {exam.name} ({slot.date})", mail_html)
            cards.append(mail_html)

            db.session.add(
                Notification(
                    user_id=student.id,
                    title=f"Reminder: {exam.name} ({slot.date})",
                    message=(
                        f"Exam: {exam.name} | Date: {slot.date} {slot.start_time}-{slot.end_time} | "
                        f"Examiner: {examiner_name} | Instructions: {instr}"
                    ),
                    notif_type="reminder",
                )
            )
            count += 1

    preview = (
        f"<div><h5>Daily Examination Reminders ({count} sent)</h5>"
        + ("".join(cards) if cards else "<p>No upcoming bookings found.</p>")
        + "</div>"
    )

    log_row = JobExecutionLog(
        job_name="daily_reminder",
        triggered_by=triggered_by,
        status="Completed",
        summary=f"Sent daily reminders for {count} upcoming booking(s).",
        html_preview=preview,
    )
    db.session.add(log_row)
    db.session.commit()

    return {
        "job": "daily_reminder",
        "reminded_count": count,
        "log_id": log_row.id,
        "summary": log_row.summary,
    }


@celery_app.task(name="tasks.generate_monthly_exam_report")
def generate_monthly_exam_report(triggered_by="celery-beat"):
    now = datetime.now(timezone.utc)
    month_name = now.strftime("%B %Y")

    total_exams = Examination.query.count()
    conducted = Examination.query.filter(Examination.status.in_(["Booking Open", "Closed", "Completed"])).count()
    evaluated = Evaluation.query.count()
    completed_bk = Booking.query.filter_by(status="Completed").count()
    active_bk = Booking.query.filter_by(status="Booked").count()

    non_cancelled = Booking.query.filter(Booking.status.in_(["Booked", "Completed"])).all()
    pending_evals = sum(1 for b in non_cancelled if not b.evaluation)

    examiners = User.query.filter_by(role="examiner").all()
    ex_rows = []
    for ex in examiners:
        s_cnt = ExaminationSlot.query.filter_by(examiner_id=ex.id).count()
        e_cnt = Evaluation.query.filter_by(examiner_id=ex.id).count()
        ex_rows.append(
            {
                "name": ex.name,
                "email": ex.email,
                "department": ex.department,
                "slots_created": s_cnt,
                "evaluations_completed": e_cnt,
                "score": s_cnt + (e_cnt * 2),
            }
        )
    ex_rows.sort(key=lambda item: item["score"], reverse=True)

    ts = now.strftime("%Y%m%d_%H%M%S")
    pdf_name = f"monthly_exam_report_{ts}.pdf"
    pdf_path = os.path.join(Config.REPORTS_FOLDER, pdf_name)

    doc = SimpleDocTemplate(pdf_path, pagesize=A4, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    story = []

    heading_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Heading1"],
        fontSize=17,
        textColor=colors.HexColor("#0d6efd"),
        spaceAfter=10,
    )
    story.append(Paragraph(f"EMP V2 - Monthly Examination Report ({month_name})", heading_style))
    story.append(Paragraph(f"Generated: {now.strftime('%Y-%m-%d %H:%M UTC')}", styles["Normal"]))
    story.append(Spacer(1, 14))

    story.append(Paragraph("Monthly Summary", styles["Heading2"]))
    stats_grid = [
        ["Metric", "Count"],
        ["Total Examinations", str(total_exams)],
        ["Examinations Conducted", str(conducted)],
        ["Students Evaluated", str(evaluated)],
        ["Completed Bookings", str(completed_bk)],
        ["Upcoming Bookings", str(active_bk)],
        ["Pending Evaluations", str(pending_evals)],
    ]
    tbl1 = Table(stats_grid, colWidths=[320, 150])
    tbl1.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0d6efd")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f8f9fa")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("PADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(tbl1)
    story.append(Spacer(1, 16))

    story.append(Paragraph("Most Active Examiners", styles["Heading2"]))
    ex_grid = [["Examiner Name", "Department", "Slots Created", "Evaluations Done"]]
    for item in ex_rows:
        ex_grid.append(
            [
                item["name"],
                item["department"] or "N/A",
                str(item["slots_created"]),
                str(item["evaluations_completed"]),
            ]
        )
    if len(ex_grid) == 1:
        ex_grid.append(["No examiners found", "-", "0", "0"])

    tbl2 = Table(ex_grid, colWidths=[160, 130, 90, 90])
    tbl2.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#198754")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("PADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(tbl2)
    doc.build(story)

    rows_html = "".join(
        f"<tr><td>{x['name']}</td><td>{x['department']}</td><td>{x['slots_created']}</td><td>{x['evaluations_completed']}</td></tr>"
        for x in ex_rows
    )
    report_html = f"""
    <div style="font-family: sans-serif; color: #212529; max-width: 780px;">
        <div style="background: #0d6efd; color: white; padding: 14px 18px; border-radius: 6px 6px 0 0;">
            <h3 style="margin: 0;">Monthly Examination Report - {month_name}</h3>
        </div>
        <div style="border: 1px solid #dee2e6; border-top: none; padding: 18px; border-radius: 0 0 6px 6px;">
            <h4>Monthly Statistics</h4>
            <table style="width: 100%; border-collapse: collapse; margin-bottom: 18px;" border="1" cellpadding="7">
                <tr style="background: #f1f5f9;"><th>Metric</th><th>Value</th></tr>
                <tr><td>Examinations Conducted</td><td><strong>{conducted}</strong> (Total: {total_exams})</td></tr>
                <tr><td>Students Evaluated</td><td><strong>{evaluated}</strong></td></tr>
                <tr><td>Completed Bookings</td><td><strong>{completed_bk}</strong></td></tr>
                <tr><td>Pending Evaluations</td><td><strong>{pending_evals}</strong></td></tr>
            </table>
            <h4>Examiner Activity</h4>
            <table style="width: 100%; border-collapse: collapse;" border="1" cellpadding="7">
                <tr style="background: #f1f5f9;">
                    <th>Examiner</th><th>Department</th><th>Slots</th><th>Evaluations</th>
                </tr>
                {rows_html or '<tr><td colspan="4">No examiner records</td></tr>'}
            </table>
        </div>
    </div>
    """

    admin = User.query.filter_by(role="admin").first()
    if admin:
        send_email_safe(
            admin.email,
            f"Monthly Examination Report - {month_name}",
            report_html,
            attachment_path=pdf_path,
        )
        db.session.add(
            Notification(
                user_id=admin.id,
                title=f"Monthly Report Generated ({month_name})",
                message=f"Conducted: {conducted} | Evaluated: {evaluated} | Completed Bookings: {completed_bk} | Pending: {pending_evals}.",
                notif_type="system",
                action_url=f"/api/admin/reports/download/{pdf_name}",
            )
        )

    log_row = JobExecutionLog(
        job_name="monthly_report",
        triggered_by=triggered_by,
        status="Completed",
        summary=(
            f"Monthly Report ({month_name}): {conducted} conducted exams, "
            f"{evaluated} evaluated students, {completed_bk} completed bookings, "
            f"{pending_evals} pending evaluations."
        ),
        artifact_path=pdf_name,
        html_preview=report_html,
    )
    db.session.add(log_row)
    db.session.commit()

    return {
        "job": "monthly_report",
        "pdf_filename": pdf_name,
        "download_url": f"/api/admin/reports/download/{pdf_name}",
        "log_id": log_row.id,
        "summary": log_row.summary,
    }


@celery_app.task(name="tasks.export_student_exam_history_csv")
def export_student_exam_history_csv(student_id):
    student = db.session.get(User, student_id)
    if not student:
        return {"error": "Student not found"}

    bookings = (
        Booking.query.filter_by(student_id=student_id)
        .order_by(Booking.booking_date.desc())
        .all()
    )

    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    fname = f"exam_history_student_{student.id}_{ts}.csv"
    fpath = os.path.join(Config.EXPORTS_FOLDER, fname)

    cols = [
        "Student ID",
        "Student Roll Number",
        "Student Name",
        "Examination Name",
        "Course",
        "Examination Date",
        "Slot Time",
        "Examiner",
        "Marks Obtained",
        "Booking Status",
    ]

    count = 0
    with open(fpath, mode="w", newline="", encoding="utf-8") as fp:
        writer = csv.writer(fp)
        writer.writerow(cols)

        for b in bookings:
            exam = b.examination
            slot = b.slot
            course_str = f"{exam.course.code} - {exam.course.name}" if (exam and exam.course) else "N/A"
            examiner_str = slot.examiner.name if (slot and slot.examiner) else "N/A"
            s_date = slot.date if slot else "N/A"
            s_time = f"{slot.start_time} - {slot.end_time}" if slot else "N/A"

            if b.evaluation and exam and exam.results_published:
                marks = f"{b.evaluation.total_marks} / {exam.max_marks}"
            elif b.evaluation:
                marks = "Awaiting Publication"
            else:
                marks = "Not Evaluated"

            writer.writerow(
                [
                    student.id,
                    student.roll_number or f"STU-{student.id:04d}",
                    student.name,
                    exam.name if exam else "N/A",
                    course_str,
                    s_date,
                    s_time,
                    examiner_str,
                    marks,
                    b.status,
                ]
            )
            count += 1

    dl_url = f"/api/student/exports/download/{fname}"

    db.session.add(
        Notification(
            user_id=student.id,
            title="CSV Export Ready",
            message=f"Your examination history CSV ({count} rows) has been exported.",
            notif_type="export",
            action_url=dl_url,
        )
    )

    log_row = JobExecutionLog(
        job_name="csv_export",
        triggered_by=f"student:{student.email}",
        status="Completed",
        summary=f"Exported {count} rows for {student.name} ({student.email}).",
        artifact_path=fname,
    )
    db.session.add(log_row)
    db.session.commit()

    return {
        "job": "csv_export",
        "student_id": student.id,
        "rows": count,
        "filename": fname,
        "download_url": dl_url,
    }


def generate_student_scorecard_pdf(booking_id):
    booking = db.session.get(Booking, booking_id)
    if not booking or not booking.evaluation:
        return None

    student = booking.student
    exam = booking.examination
    slot = booking.slot
    ev = booking.evaluation
    ev_data = ev.to_dict()

    fname = f"scorecard_booking_{booking.id}.pdf"
    fpath = os.path.join(Config.REPORTS_FOLDER, fname)

    doc = SimpleDocTemplate(fpath, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    story = []

    head_style = ParagraphStyle(
        "ScorecardTitle",
        parent=styles["Heading1"],
        fontSize=19,
        textColor=colors.HexColor("#0d6efd"),
        spaceAfter=6,
    )
    story.append(Paragraph("EXAMINATION SCORECARD", head_style))
    story.append(Paragraph("Examination Management Portal - V2", styles["Italic"]))
    story.append(Spacer(1, 14))

    meta_rows = [
        ["Student Name:", student.name, "Roll Number:", student.roll_number or f"STU-{student.id:04d}"],
        ["Email:", student.email, "Department:", student.department or "N/A"],
        ["Course:", f"{exam.course.code} - {exam.course.name}" if exam.course else "N/A", "Exam Type:", exam.exam_type],
        ["Examination:", exam.name, "Exam Date:", f"{slot.date} ({slot.start_time}-{slot.end_time})" if slot else "N/A"],
        ["Examiner:", slot.examiner.name if (slot and slot.examiner) else "N/A", "Booking ID:", f"#{booking.id}"],
    ]
    meta_tbl = Table(meta_rows, colWidths=[100, 170, 95, 145])
    meta_tbl.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#e9ecef")),
                ("BACKGROUND", (2, 0), (2, -1), colors.HexColor("#e9ecef")),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("PADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(meta_tbl)
    story.append(Spacer(1, 16))

    story.append(Paragraph("Rubric Breakdown", styles["Heading2"]))
    rubric_grid = [["Criterion", "Weightage (%)", "Max Marks", "Awarded", "Comment"]]
    for item in ev_data.get("rubric_breakdown", []):
        rubric_grid.append(
            [
                str(item.get("criterion_name", "")),
                f"{item.get('weightage', 0)}%",
                str(item.get("max_marks", 0)),
                str(item.get("marks_awarded", 0)),
                str(item.get("comment", "-")),
            ]
        )
    if len(rubric_grid) == 1:
        rubric_grid.append(["Overall Assessment", "100%", str(exam.max_marks), str(ev.total_marks), ev.remarks or "-"])

    r_tbl = Table(rubric_grid, colWidths=[140, 75, 70, 85, 140])
    r_tbl.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0d6efd")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("PADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(r_tbl)
    story.append(Spacer(1, 16))

