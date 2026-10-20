# Examination Management Portal - V2

Web application for managing courses, examinations, examiner slot schedules, student slot bookings, rubric evaluations, and result scorecards.

## Tech Stack
- **Backend:** Flask, Flask-SQLAlchemy, Flask-JWT-Extended, Flask-CORS, SQLite, Redis, Celery, ReportLab
- **Frontend:** Vue 3 (Vue CLI), Bootstrap 5, Chart.js

## Project Structure
- `backend/` — Flask API, SQLAlchemy models, Redis cache helper, Celery tasks, and seed script
- `frontend/` — Vue CLI Single-File Components (`src/App.vue`, `src/components/*.vue`)

## Setup & Run

### Backend (Port 5000)
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
python backend/app.py
```

### Frontend (Port 8000)
```bash
cd frontend
npm install
npm run serve
```
