"""Shared RAG helpers: retrieval context building and URL extraction.

Used by the Flask routes (``/chat``, ``/chat-sse``, ``/query``) and by the
``query_collection_tool`` LangChain tool, which used to carry four copies of the
same retrieve-then-format logic.
"""

import logging
import re
from typing import Any, Dict, Iterable, List, Optional, Tuple

from backend.vectoreStoreClient.chromaDBclient import get_client

logger = logging.getLogger(__name__)

# Upper bound on the retrieved context, in characters. Chroma documents are whole
# chunks: without a budget a large nResults inflates the prompt and the bill.
MAX_CONTEXT_CHARS = 12000

_URL_RE = re.compile(r"https?://[^\s<>\"')]+", re.IGNORECASE)
_ALLOWED_ROLES = ("system", "user", "assistant")


def _flatten_chunks(values: Any) -> List[str]:
    """Flatten a Chroma `query` result (list per query text) into a flat list."""
    if not values:
        return []
    if isinstance(values, str):
        return [values]
    first = values[0]
    if isinstance(first, (list, tuple)):
        return [chunk for chunk in first if isinstance(chunk, str)]
    return [values] if isinstance(values, str) else []


def render_context(
    documents: Any,
    metadatas: Any = None,
    max_chars: int = MAX_CONTEXT_CHARS,
) -> str:
    """Render retrieved chunks as a single text block, within a char budget."""
    chunks = _flatten_chunks(documents)
    if not chunks:
        return ""

    # Metadata entries are dicts, so they are unwrapped separately from the
    # string chunks to survive a non-nested result shape.
    meta_values: List[Dict] = []
    if metadatas:
        candidate = metadatas[0] if isinstance(metadatas[0], (list, tuple)) else metadatas
        meta_values = [m for m in candidate if isinstance(m, dict)]

    parts: List[str] = []
    used = 0
    for index, chunk in enumerate(chunks):
        source = ""
        if index < len(meta_values):
            meta = meta_values[index]
            source = str(meta.get("source") or meta.get("fileName") or meta.get("app") or "")
        header = f"[{index + 1}]" + (f" {source}" if source else "")
        block = f"{header}\n{chunk}"

        if used + len(block) > max_chars:
            remaining = max_chars - used
            if remaining > 200:
                parts.append(block[:remaining])
            logger.info("Context truncated at %d/%d chars (%d chunks kept)",
                        max_chars, used + len(block), len(parts))
            break

        parts.append(block)
        used += len(block)

    return "\n\n".join(parts)


def build_context_messages(
    query: str,
    history: Optional[Iterable[Dict[str, Any]]] = None,
    use_vectorstore: bool = False,
    n_results: int = 5,
    include: Optional[List[str]] = None,
    where: Optional[Dict] = None,
) -> Tuple[List[Dict[str, str]], List[List[str]], List[List[Dict]]]:
    """Build the LLM message list for a request.

    Returns ``(messages, documents, metadatas)``. The retrieved context is
    injected as a *single* leading system message: the previous code appended
    one `system` message per chunk after the user history, which is invalid
    ordering for providers that require the system message first (Mistral).
    """
    messages: List[Dict[str, str]] = []
    documents: List[List[str]] = []
    metadatas: List[List[Dict]] = []

    if use_vectorstore:
        try:
            result = get_client().query_collection(
                query_texts=[query],
                n_results=n_results,
                include=include,
                where=where,
            )
        except Exception:
            # A retrieval failure must not take the whole chat down.
            logger.exception("Vectorstore lookup failed for query %r", query)
        else:
            documents = result.get("documents") or []
            metadatas = result.get("metadatas") or []
            context = render_context(documents, metadatas)
            if context:
                messages.append({
                    "role": "system",
                    "content": "Contexte documentaire retrieved:\n" + context,
                })
            else:
                logger.info("Vectorstore returned no context for query %r", query)

    for item in history or []:
        if not isinstance(item, dict):
            continue
        role = item.get("role")
        content = item.get("content")
        if role in _ALLOWED_ROLES and isinstance(content, str) and content.strip():
            messages.append({"role": role, "content": content})

    messages.append({"role": "user", "content": query})
    return messages, documents, metadatas


def extract_urls(text: str) -> List[str]:
    """Return the distinct http(s) URLs contained in `text`, in order."""
    if not text:
        return []
    seen: List[str] = []
    for match in _URL_RE.findall(text):
        url = match.rstrip(".,;:!?")
        if url not in seen:
            seen.append(url)
    return seen
