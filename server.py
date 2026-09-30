import json
import logging
import os

from flask import Flask, jsonify, request, send_from_directory, Response, stream_with_context
from flask_cors import CORS

from backend.rag import build_context_messages, extract_urls
from backend.vectoreStoreClient.chromaDBclient import get_client
from backend.youtube.youtubeToText import Youtube
from backend.ai.agent import AIProviderManager

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Lazy singletons: importing this module no longer opens the Chroma store, so a
# syntax check, a CLI run or a failed startup does not pay for it.
_transcript = None
_agent = None


def transcript():
    global _transcript
    if _transcript is None:
        _transcript = Youtube()
    return _transcript


def agent():
    global _agent
    if _agent is None:
        _agent = AIProviderManager()
    return _agent


def read_json():
    """Return the request body, or a 400 response when it is absent/invalid."""
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return None, (jsonify({"error": "Expected a JSON object body"}), 400)
    return data, None


def parse_where(raw):
    """Parse the `metadatas` query-string filter into a Chroma `where` dict."""
    if not raw:
        return None
    try:
        value = json.loads(raw)
    except (TypeError, ValueError):
        raise ValueError("'metadatas' must be a JSON object")
    if not isinstance(value, dict):
        raise ValueError("'metadatas' must be a JSON object")
    return value


@app.route('/')
def index():
    return send_from_directory('dist', 'index.html')


@app.route("/<path:path>")
def home(path):
    return send_from_directory('dist', path)


@app.route('/assets/guide_utilisateur.pdf')
def guide_utilisateur():
    return send_from_directory('src/assets', 'guide_utilisateur.pdf')


# --- SSE Streaming Endpoint ---
@app.route('/chat-sse', methods=['POST'])
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
            # Closes the upstream generator so the Ollama/Mistral HTTP
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


@app.route('/chat', methods=['POST'])
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


@app.route('/initialize', methods=['POST'])
def initialize():
    try:
        get_client().initialize()
        return jsonify({"message": "Collection initialized"}), 200
    except Exception:
        logger.exception("Error initializing collection")
        return jsonify({"error": "Error initializing collection"}), 500


@app.route('/documents', methods=['POST'])
def add_documents():
    data, error = read_json()
    if error:
        return error

    try:
        get_client().add_document(
            documents=data.get('documents') or [],
            ids=data.get('ids') or [],
            metadatas=data.get('metadatas'),
        )
        return jsonify({"message": "Documents added"}), 200
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception:
        logger.exception("Error adding documents")
        return jsonify({"error": "Error adding documents"}), 500


@app.route('/query', methods=['POST'])
def query_collection():
    data, error = read_json()
    if error:
        return error

    query_texts = data.get('queryTexts')
    if not query_texts or not isinstance(query_texts, list):
        return jsonify({"error": "Field 'queryTexts' must be a non-empty list"}), 400

    try:
        results = get_client().query_collection(
            query_texts=query_texts,
            n_results=data.get('nResults', 10),
            include=data.get('include') or None,
            where=data.get('metadatas'),
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception:
        logger.exception("Error querying collection")
        return jsonify({"error": "Error querying collection"}), 500

    # Attach transcripts / page content for the URLs mentioned in the query.
    if not results["metadatas"]:
        results["metadatas"] = [[]]
    for url in extract_urls(query_texts[0]):
        try:
            if "youtube.com" in url or "youtu.be" in url:
                text = transcript().generateText(url)
                results["metadatas"][0].append({"transcript": text})
            else:
                text = transcript().generateMArkdown(url)
                results["metadatas"][0].append({"web page": text})
        except Exception:
            logger.warning("Could not fetch content for %s", url, exc_info=True)
            results["metadatas"][0].append({"error": f"Could not fetch {url}"})

    return jsonify(results), 200


@app.route('/documents', methods=['GET'])
def get_documents():
    ids = request.args.get('ids')
    include_list = request.args.get('include')
    include = (
        [item.strip() for item in include_list.split(',') if item.strip()]
        if include_list else None
    )

    try:
        where = parse_where(request.args.get('metadatas'))
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    try:
        results = get_client().get_document(
            ids=ids.split(',') if ids else None,
            include=include,
            where=where,
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception:
        logger.exception("Error getting documents")
        return jsonify({"error": "Error getting documents"}), 500

    logger.debug("GET /documents returned %d document(s)", len(results))
    return jsonify({"documents": results}), 200


@app.route('/documents', methods=['PUT'])
def update_documents():
    data, error = read_json()
    if error:
        return error

    try:
        get_client().update_document(
            ids=data.get('ids') or [],
            documents=data.get('documents') or [],
        )
        return jsonify({"message": "Documents updated"}), 200
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception:
        logger.exception("Error updating documents")
        return jsonify({"error": "Error updating documents"}), 500


@app.route('/documents', methods=['DELETE'])
def delete_documents():
    data, error = read_json()
    if error:
        return error

    ids = data.get('ids')
    if not ids:
        return jsonify({"error": "Field 'ids' is required"}), 400

    try:
        get_client().delete_document(ids)
        return jsonify({"message": "Documents deleted"}), 200
    except Exception:
        logger.exception("Error deleting documents")
        return jsonify({"error": "Error deleting documents"}), 500


@app.route('/empty-documents', methods=['DELETE'])
def delete_all_documents():
    try:
        where = parse_where(request.args.get('metadatas'))
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    try:
        get_client().delete_all_documents(where)
        return jsonify({"message": "success"}), 200
    except Exception:
        logger.exception("Error deleting documents")
        return jsonify({"error": "Error deleting documents"}), 500


if __name__ == '__main__':
    # debug=True on 0.0.0.0 exposes the Werkzeug debugger and starts a second
    # process that reopens the same chroma_store directory.
    app.run(
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", 3000)),
        debug=os.getenv("FLASK_DEBUG", "").lower() in ("1", "true", "yes"),
    )
