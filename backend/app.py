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
    if test_config:
        app.config.update(test_config)

    CORS(app)
    db.init_app(app)
    JWTManager(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(examiner_bp)
    app.register_blueprint(student_bp)

    @app.route("/api/health", methods=["GET"])
    def health():
        return jsonify({
            "status": "ok",
            "application": "Examination Management Portal - V2",
            "cache": get_cache_info(),
        }), 200
