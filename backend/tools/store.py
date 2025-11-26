from backend.vectoreStoreClient.chromaDBclient import ChromaDBClient
from backend.youtube.youtubeToText import Youtube

chroma_db_client = ChromaDBClient("my_collection")

transcript = Youtube()


def query_collection_tool(input_data: dict):
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

    try:
        query_texts = input_data.get("queryTexts")
        n_results = input_data.get("nResults", 10)
        include = input_data.get("include", [])
        metadatas = input_data.get("metadatas")

        # Query the DB
        results = chroma_db_client.query_collection(
            query_texts=query_texts,
            n_results=n_results,
            include=include,
            metadatas=metadatas
        )

        # Post-processing: detect URLs in the first query text
        first_query = query_texts[0] if query_texts else ""
        for t in first_query.split(" "):
            if "metadatas" not in results or not results["metadatas"]:
                continue

            # If youtube link → add transcript
            if t.startswith("http") and "youtube.com" in t:
                text = transcript.generateText(t)
                results["metadatas"][0].append({"transcript": text})

            # If non-youtube URL → add webpage markdown
            elif t.startswith("http"):
                text = transcript.generateMArkdown(t)
                results["metadatas"][0].append({"web page": text})

        return results

    except Exception as e:
        return {"error": f"Error querying collection: {e}"}
