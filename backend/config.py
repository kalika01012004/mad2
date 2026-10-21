import os
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, "instance")
EXPORTS_DIR = os.path.join(INSTANCE_DIR, "exports")
REPORTS_DIR = os.path.join(INSTANCE_DIR, "reports")

for folder in (INSTANCE_DIR, EXPORTS_DIR, REPORTS_DIR):
    os.makedirs(folder, exist_ok=True)


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "mad2-emp-v2-secret-key")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(INSTANCE_DIR, 'emp_v2.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "mad2-emp-v2-jwt-signing-secret-key-2026")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)

    REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    CACHE_DEFAULT_TIMEOUT = int(os.environ.get("CACHE_DEFAULT_TIMEOUT", 120))
