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
