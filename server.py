"""Backend entry point.

`server:app` (gunicorn, see deploy/systemd/chatbot-backend.service) and
`python server.py` (development) both use the same application object; the
routes themselves live in `backend/api/`.
"""

import logging
import os

from backend.api.app import create_app

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
)

app = create_app()


if __name__ == '__main__':
    # debug=True on 0.0.0.0 exposes the Werkzeug debugger and starts a second
    # process that reopens the same chroma_store directory.
    app.run(
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", 3000)),
        debug=os.getenv("FLASK_DEBUG", "").lower() in ("1", "true", "yes"),
    )
