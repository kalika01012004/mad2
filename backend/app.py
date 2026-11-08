import os
from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from config import Config
from models import db
from seed import init_db_and_seed
from cache import get_cache_info
from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.examiner import examiner_bp
from routes.student import student_bp

DIST_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "dist"))


def create_app(test_config=None, seed_demo=True):
    app = Flask(__name__, static_folder=DIST_DIR, static_url_path="")
    app.config.from_object(Config)
