"""Document routes: `/documents`, `/query`, `/initialize`, `/empty-documents`."""

import logging

from flask import Blueprint, jsonify, request

from backend.api.common import parse_where, read_json
from backend.rag import extract_urls
from backend.vectorestore.chroma_client import get_client
from backend.youtube.youtubeToText import get_transcript

logger = logging.getLogger(__name__)

documents_bp = Blueprint("documents", __name__)


@documents_bp.route('/initialize', methods=['POST'])
def initialize():
    try:
        get_client().initialize()
        return jsonify({"message": "Collection initialized"}), 200
    except Exception:
        logger.exception("Error initializing collection")
        return jsonify({"error": "Error initializing collection"}), 500


@documents_bp.route('/documents', methods=['POST'])
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


@documents_bp.route('/query', methods=['POST'])
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
                text = get_transcript().generateText(url)
                results["metadatas"][0].append({"transcript": text})
            else:
                text = get_transcript().generateMArkdown(url)
                results["metadatas"][0].append({"web page": text})
        except Exception:
            logger.warning("Could not fetch content for %s", url, exc_info=True)
            results["metadatas"][0].append({"error": f"Could not fetch {url}"})

    return jsonify(results), 200


@documents_bp.route('/documents', methods=['GET'])
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


@documents_bp.route('/documents', methods=['PUT'])
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


@documents_bp.route('/documents', methods=['DELETE'])
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


@documents_bp.route('/empty-documents', methods=['DELETE'])
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
