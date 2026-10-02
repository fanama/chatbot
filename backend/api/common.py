"""Helpers shared by the HTTP routes."""

import json
from typing import Any, Dict, Optional, Tuple

from flask import jsonify, request


def read_json() -> Tuple[Optional[Dict[str, Any]], Any]:
    """Return the request body, or a 400 response when it is absent/invalid."""
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return None, (jsonify({"error": "Expected a JSON object body"}), 400)
    return data, None


def parse_where(raw: Optional[str]) -> Any:
    """Parse the `metadatas` query-string filter into a Chroma `where` dict."""
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except (TypeError, ValueError):
        raise ValueError("'metadatas' must be a valid JSON object")
