"""Flask application factory.

Wiring only: the route logic lives in the `chat` and `documents` blueprints.
"""

from pathlib import Path

from flask import Flask, send_from_directory
from flask_cors import CORS

from backend.api.chat import chat_bp
from backend.api.documents import documents_bp

# `send_from_directory` resolves a relative directory against the app root path,
# which is `backend/api/` now that the factory lives here (it used to be the
# repository root, when everything was in `server.py`). Absolute paths also make
# the app independent from the working directory it was started with.
PROJECT_ROOT = Path(__file__).resolve().parents[2]


def create_app() -> Flask:
    """Build the app; `server:app` (gunicorn) and `python server.py` both use it."""
    app = Flask(__name__)

    # Open CORS: fine for local development, but restrict it to the frontend
    # origin before deploying.
    CORS(app)

    # --- Static assets (built frontend) ---
    @app.route('/')
    def index():
        return send_from_directory(PROJECT_ROOT / 'dist', 'index.html')

    @app.route('/<path:path>')
    def home(path):
        return send_from_directory(PROJECT_ROOT / 'dist', path)

    @app.route('/assets/guide_utilisateur.pdf')
    def guide_utilisateur():
        return send_from_directory(PROJECT_ROOT / 'src/assets', 'guide_utilisateur.pdf')

    app.register_blueprint(chat_bp)
    app.register_blueprint(documents_bp)
    return app
