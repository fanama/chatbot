from chromadb import PersistentClient, HttpClient, Collection
from chromadb.utils import embedding_functions
from typing import List, Dict, Optional, Union

# Configure embedding function
embed_fn = embedding_functions.DefaultEmbeddingFunction()


class ChromaDBClient:
    def __init__(self, collection_name: str = "test"):
        # Store data persistently in a folder
        self.client = PersistentClient(path="./chroma_store")
        # self.client = HttpClient()
        self.collection_name = collection_name
        self.collection: Optional[Collection] = None
        self.initialize()

    def initialize(self) -> None:
        """Initialize (or get) the ChromaDB collection with embeddings."""
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=embed_fn
        )

    def add_document(
        self,
        documents: List[str],
        ids: List[str],
        metadatas: Optional[List[Dict[str, Union[str, int, bool]]]] = None
    ) -> None:
        """Add documents to the ChromaDB collection."""
        if self.collection is None:
            self.initialize()
        metadatas = metadatas or [{}] * len(documents)

        # Let ChromaDB handle embeddings automatically
        self.collection.add(
            documents=documents,
            ids=ids,
            metadatas=metadatas
        )

        # Debug: show stored data
        # results = self.collection.get(include=[ "documents", "metadatas", "embeddings"])
        # print("📥 Document added. Current store:", results)

    def query_collection(
        self,
        query_texts: List[str],
        n_results: int = 10,
        include: Optional[List[str]] = None,
        metadatas: Optional[Dict] = None
    ) -> Dict:
        """Query the collection for similar documents."""

        print("🔍 Query input:", query_texts)

        if self.collection is None:
            self.initialize()
        if include is None:
            include = ["documents", "metadatas"]

        # Debug: see all stored docs before querying
        docs_snapshot = self.collection.get(
            include=["documents", "embeddings"])
        embeddings = docs_snapshot.get("embeddings")
        # print("📂 All documents :", docs_snapshot.get('documents'))
        if embeddings is not None:
            print("📂 All documents embeddings shape:", embeddings.shape)
        else:
            print("⚠ No embeddings found in collection")

        result = self.collection.query(
            query_texts=query_texts,
            n_results=n_results,
            include=["documents", "metadatas"],
            where=metadatas
        )

        # print("🎯 Query result:", result.get('documents'))
        return {
            "documents": result.get("documents") or [],
            "metadatas": result.get("metadatas") or []
        }

    def get_document(
        self,
        ids: Optional[List[str]] = None,
        include: Optional[List[str]] = None,
        metadatas: Optional[Dict] = None
    ) -> List[str]:
        """Retrieve documents by ID or metadata."""
        if self.collection is None:
            self.initialize()
        if include is None:
            include = ["documents", "metadatas", "ids"]

        print("📄 Getting documents", {"ids": ids,
              "include": include, "filter": metadatas})
        results = self.collection.get(
            ids=ids, include=include, where=metadatas)
        return results.get("documents") or []

    def get_document_id(
        self,
        ids: Optional[Union[str, List[str]]] = None,
        include: Optional[List[str]] = None,
        metadatas: Optional[Dict] = None
    ) -> List[str]:
        """Return the IDs of matching documents."""
        if self.collection is None:
            self.initialize()
        results = self.collection.get(
            ids=ids, include=include, where=metadatas)
        return results.get("ids", [])

    def update_document(self, ids: List[str], documents: List[str]) -> None:
        """Update documents by ID."""
        if self.collection is None:
            self.initialize()
        self.collection.update(ids=ids, documents=documents)

    def delete_document(self, ids: List[str]) -> None:
        """Delete specific documents."""
        if self.collection is None:
            self.initialize()
        self.collection.delete(ids=ids)

    def delete_all_documents(self, metadatas: Optional[Dict] = None) -> None:
        """Delete all documents (or those matching metadata)."""
        if self.collection is None:
            self.initialize()
        all_ids = self.get_document_id(
            include=["metadatas"], metadatas=metadatas)
        if all_ids:
            self.delete_document(all_ids)
