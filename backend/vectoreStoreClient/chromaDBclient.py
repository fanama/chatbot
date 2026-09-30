import logging
import threading
from typing import Dict, List, Optional, Union

from chromadb import PersistentClient, Collection
from chromadb.utils import embedding_functions

logger = logging.getLogger(__name__)

# Configure embedding function
embed_fn = embedding_functions.DefaultEmbeddingFunction()

DEFAULT_INCLUDE = ["documents", "metadatas"]
# Chroma rejects anything outside this set (chromadb/api/types.py::Include),
# so never forward a caller-supplied value without filtering it.
ALLOWED_INCLUDE = {"documents", "embeddings", "metadatas", "distances", "uris", "data"}
# Chroma refuses payloads larger than this (max_batch_size).
BATCH_SIZE = 500


def _sanitize_include(include: Optional[List[str]]) -> List[str]:
    """Keep only include values Chroma accepts, deduplicated and ordered."""
    if not include:
        return list(DEFAULT_INCLUDE)
    valid = [item for item in dict.fromkeys(include) if item in ALLOWED_INCLUDE]
    if not valid:
        return list(DEFAULT_INCLUDE)
    return valid


def _clamp_n_results(n_results: Optional[int], fallback: int = 10) -> int:
    """Chroma requires a strictly positive n_results; clamp instead of crashing."""
    try:
        value = int(n_results)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return fallback
    return max(1, min(value, BATCH_SIZE))


class ChromaDBClient:
    def __init__(self, collection_name: str = "test"):
        # Store data persistently in a folder
        self.client = PersistentClient(path="./chroma_store")
        self.collection_name = collection_name
        self.collection: Optional[Collection] = None
        # Guards collection (re)creation so concurrent requests cannot race on
        # get_or_create_collection against the same on-disk store.
        self._lock = threading.Lock()
        self.initialize()

    def initialize(self) -> None:
        """Initialize (or get) the ChromaDB collection with embeddings."""
        with self._lock:
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                embedding_function=embed_fn
            )

    def _require_collection(self) -> Collection:
        if self.collection is None:
            self.initialize()
        assert self.collection is not None  # narrowed for type checkers
        return self.collection

    def add_document(
        self,
        documents: List[str],
        ids: List[str],
        metadatas: Optional[List[Dict[str, Union[str, int, bool]]]] = None
    ) -> None:
        """Add documents to the ChromaDB collection."""
        if not documents:
            return
        if len(documents) != len(ids):
            raise ValueError(
                f"documents and ids must have the same length "
                f"({len(documents)} != {len(ids)})"
            )

        collection = self._require_collection()
        metadatas = metadatas or [{}] * len(documents)

        # Let ChromaDB handle embeddings automatically, in batches so we never
        # exceed the server-side max_batch_size.
        for start in range(0, len(documents), BATCH_SIZE):
            end = start + BATCH_SIZE
            collection.add(
                documents=documents[start:end],
                ids=ids[start:end],
                metadatas=metadatas[start:end],
            )
        logger.info("Added %d document(s) to '%s'", len(documents), self.collection_name)

    def query_collection(
        self,
        query_texts: List[str],
        n_results: int = 10,
        include: Optional[List[str]] = None,
        where: Optional[Dict] = None,
    ) -> Dict:
        """Query the collection for similar documents.

        `where` is a Chroma filter expression, not document metadata.
        """
        if not query_texts:
            return {"documents": [], "metadatas": []}

        collection = self._require_collection()
        include = _sanitize_include(include)
        n_results = _clamp_n_results(n_results)

        logger.debug("Query '%s' n_results=%s where=%s", query_texts, n_results, where)

        result = collection.query(
            query_texts=query_texts,
            n_results=n_results,
            include=include,
            where=where or None,
        )

        return {
            "documents": result.get("documents") or [],
            "metadatas": result.get("metadatas") or [],
        }

    def get_document(
        self,
        ids: Optional[List[str]] = None,
        include: Optional[List[str]] = None,
        where: Optional[Dict] = None,
    ) -> List[Dict[str, str]]:
        """Retrieve documents by ID or metadata filter.

        Returns one dict per document (ids are always part of a `get` result,
        they are not a valid `include` value).
        """
        collection = self._require_collection()
        include = _sanitize_include(include)

        results = collection.get(ids=ids, include=include, where=where or None)
        return self._zip_results(results)

    def get_document_id(
        self,
        ids: Optional[Union[str, List[str]]] = None,
        where: Optional[Dict] = None,
    ) -> List[str]:
        """Return the IDs of matching documents."""
        collection = self._require_collection()
        if isinstance(ids, str):
            ids = ids.split(",")

        logger.debug("Getting document ids where=%s", where)
        results = collection.get(ids=ids, include=["metadatas"], where=where or None)
        return results.get("ids") or []

    @staticmethod
    def _zip_results(results: Dict) -> List[Dict[str, str]]:
        """Flatten a Chroma `get` result into a list of per-document dicts."""
        if not results:
            return []

        total = len(results.get("ids") or [])
        documents = results.get("documents") or []
        metadatas = results.get("metadatas") or []

        out: List[Dict[str, str]] = []
        for index in range(total):
            entry: Dict[str, str] = {"id": results["ids"][index]}
            if index < len(documents) and documents[index] is not None:
                entry["document"] = documents[index]
            if index < len(metadatas) and metadatas[index] is not None:
                entry["metadata"] = metadatas[index]
            out.append(entry)
        return out

    def update_document(self, ids: List[str], documents: List[str]) -> None:
        """Update documents by ID."""
        if len(ids) != len(documents):
            raise ValueError(
                f"ids and documents must have the same length "
                f"({len(ids)} != {len(documents)})"
            )
        collection = self._require_collection()
        for start in range(0, len(ids), BATCH_SIZE):
            end = start + BATCH_SIZE
            collection.update(ids=ids[start:end], documents=documents[start:end])

    def delete_document(self, ids: List[str]) -> None:
        """Delete specific documents."""
        if not ids:
            return
        collection = self._require_collection()
        for start in range(0, len(ids), BATCH_SIZE):
            end = start + BATCH_SIZE
            collection.delete(ids=ids[start:end])

    def delete_all_documents(self, where: Optional[Dict] = None) -> None:
        """Delete all documents (or those matching a metadata filter)."""
        all_ids = self.get_document_id(where=where)
        if all_ids:
            self.delete_document(all_ids)
        logger.info("Deleted %d document(s) from '%s'", len(all_ids), self.collection_name)


# Single shared handle: server.py and tools/store.py used to build two separate
# ChromaDBClient objects over the same on-disk collection.
_client_lock = threading.Lock()
_client: Optional[ChromaDBClient] = None


def get_client(collection_name: str = "my_collection") -> ChromaDBClient:
    """Return the process-wide ChromaDBClient, creating it on first use."""
    global _client
    if _client is None:
        with _client_lock:
            if _client is None:
                _client = ChromaDBClient(collection_name)
    return _client
