import logging
from typing import Any, Dict

from backend.rag import extract_urls
from backend.vectoreStoreClient.chromaDBclient import get_client
from backend.youtube.youtubeToText import Youtube

logger = logging.getLogger(__name__)

_transcript = None


def transcript() -> Youtube:
    global _transcript
    if _transcript is None:
        _transcript = Youtube()
    return _transcript


def query_collection_tool(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Query a ChromaDB collection and optionally attach transcripts or markdown
    for URLs found inside the query text.
    Query information before websearch

    Expected input format:
    {
        "queryTexts": ["..."],
        "nResults": 10,
        "include": [],
        "metadatas": {...}
    }
    """
    if not isinstance(input_data, dict):
        return {"error": "Input must be an object"}

    query_texts = input_data.get("queryTexts")
    if not query_texts or not isinstance(query_texts, list):
        return {"error": "Field 'queryTexts' must be a non-empty list"}

    try:
        results = get_client().query_collection(
            query_texts=query_texts,
            n_results=input_data.get("nResults", 10),
            include=input_data.get("include") or None,
            where=input_data.get("metadatas"),
        )
    except Exception as exc:
        logger.exception("Tool query_collection failed")
        return {"error": f"Error querying collection: {exc}"}

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

    return results
