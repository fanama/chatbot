"""Chat routes: buffered `/chat` and streaming `/chat-sse`."""

import json
import logging

from flask import Blueprint, Response, jsonify, stream_with_context

from backend.ai.agent import AIProviderManager
from backend.api.common import read_json
from backend.rag import build_context_messages

logger = logging.getLogger(__name__)

chat_bp = Blueprint("chat", __name__)

# Lazy singleton: building the manager opens nothing heavy, but importing this
# module must stay cheap for a syntax check or a CLI run.
_agent = None


def agent():
    global _agent
    if _agent is None:
        _agent = AIProviderManager()
    return _agent


@chat_bp.route("/chat-sse", methods=["POST"])
def chat_sse():
    data, error = read_json()
    if error:
        return error

    query = data.get("query")
    if not query or not isinstance(query, str):
        return jsonify({"error": "Field 'query' is required"}), 400

    messages, _documents, _metadatas = build_context_messages(
        query=query,
        history=data.get("history") or [],
        use_vectorstore=data.get("useVectorstore", True),
        n_results=data.get("nResults", 5),
        include=data.get("include") or None,
        where=data.get("metadatas"),
    )

    def sse(payload: dict) -> str:
        return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"

    def generate_stream():
        stream = agent().call_stream(messages)
        try:
            for kind, value in stream:
                if kind == "provider":
                    # Sent before any token so the client can label the answer.
                    yield sse({"type": "provider", "provider": value})
                else:
                    yield sse({"type": "text", "text": value})
        except GeneratorExit:
            # Client disconnected mid-stream.
            logger.info("Client disconnected during streaming")
            return
        except Exception:
            logger.exception("Streaming failed")
            yield sse({"type": "error", "text": "Erreur interne pendant la génération."})
        finally:
            # Closes the upstream generator so the Mistral/Ollama HTTP
            # connection is released instead of waiting for the GC.
            close = getattr(stream, "close", None)
            if close:
                close()

        # Reached only on normal completion or on a handled error: a yield in a
        # finally block would raise RuntimeError on client disconnect.
        yield "data: [DONE]\n\n"

    response = Response(
        stream_with_context(generate_stream()),
        mimetype="text/event-stream",
    )
    # Without these, nginx buffers the stream and tokens arrive in bursts.
    response.headers["Cache-Control"] = "no-cache, no-transform"
    response.headers["X-Accel-Buffering"] = "no"
    response.headers["Connection"] = "keep-alive"
    return response


@chat_bp.route("/chat", methods=["POST"])
def chatbot():
    data, error = read_json()
    if error:
        return error

    query = data.get("query")
    if not query or not isinstance(query, str):
        return jsonify({"error": "Field 'query' is required"}), 400

    messages, documents, metadatas = build_context_messages(
        query=query,
        use_vectorstore=data.get("useVectorstore", True),
        n_results=data.get("nResults", 5),
        include=data.get("include") or None,
        where=data.get("metadatas"),
    )

    return jsonify({
        "message": agent().call(messages),
        "documents": documents,
        "metadatas": metadatas,
    }), 200
