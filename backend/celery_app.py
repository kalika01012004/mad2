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
