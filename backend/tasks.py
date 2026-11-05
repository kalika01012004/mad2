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
