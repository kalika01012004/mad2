from celery import Celery
from celery.schedules import crontab
from config import Config

celery_app = Celery(
    "emp_v2_tasks",
    broker=Config.CELERY_BROKER_URL,
    backend=Config.CELERY_RESULT_BACKEND,
    include=["tasks"],
)

celery_app.conf.update(
    timezone="Asia/Kolkata",
    enable_utc=True,
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    task_always_eager=Config.CELERY_TASK_ALWAYS_EAGER,
    beat_schedule={
        "daily-examination-reminder-job": {
            "task": "tasks.send_daily_exam_reminders",
            "schedule": crontab(hour=8, minute=0),
        },
        "monthly-examination-report-job": {
            "task": "tasks.generate_monthly_exam_report",
            "schedule": crontab(day_of_month=1, hour=9, minute=0),
        },
    },
)
