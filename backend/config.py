import os
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, "instance")
EXPORTS_DIR = os.path.join(INSTANCE_DIR, "exports")
REPORTS_DIR = os.path.join(INSTANCE_DIR, "reports")

for folder in (INSTANCE_DIR, EXPORTS_DIR, REPORTS_DIR):
    os.makedirs(folder, exist_ok=True)


