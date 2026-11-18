# Examination Management Portal - V2

Web application for managing courses, examinations, examiner slot schedules, student slot bookings, rubric evaluations, and result scorecards.

## Author & Demo
- **Name:** Kalika (`23F2004007`)
- **Email:** `23f2004007@ds.study.iitm.ac.in`
- **Demo Walkthrough Video:** https://drive.google.com/file/d/13-hTfwxfiARkfi-AFc5idFN3pVQN2byJ/view?usp=sharing

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
