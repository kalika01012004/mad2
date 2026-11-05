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
