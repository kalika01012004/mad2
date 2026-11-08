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

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def index_route(path):
        if path and os.path.exists(os.path.join(DIST_DIR, path)):
            return send_from_directory(DIST_DIR, path)
        idx = os.path.join(DIST_DIR, "index.html")
        if os.path.exists(idx):
            return send_from_directory(DIST_DIR, "index.html")
        return jsonify({"status": "running", "application": "Examination Management Portal - V2"}), 200

    init_db_and_seed(app, seed_demo_data=seed_demo)
    return app


app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="127.0.0.1", port=port, debug=True, use_reloader=False)
