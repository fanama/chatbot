from flask import Flask, request, jsonify, send_from_directory,  stream_with_context, Response
from flask_cors import CORS
from backend.vectoreStoreClient.chromaDBclient import ChromaDBClient
from backend.youtube.youtubeToText import Youtube
from backend.ai.agent import AIProviderManager

import json


app = Flask(__name__)
CORS(app)

chroma_db_client = ChromaDBClient("my_collection")
transcript = Youtube()
agent = AIProviderManager()


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
    req = request.get_json()

    query = req.get("query")
    history = req.get("history", [])
    n_results = req.get("nResults", 5)
    include = req.get("include", [])
    metadatas = req.get("metadatas")
    use_vectorstore = req.get("useVectorstore", False)  # NEW FLAG

    if not query:
        return jsonify({"message": "QUERY is empty"}), 429

    documents = []
    metadatas_db = []

    # --- OPTIONAL VECTORSTORE LOOKUP ---
    if use_vectorstore:
        vs = chroma_db_client.query_collection(
            [query],
            n_results,
            include,
            metadatas
        )
        documents = vs.get("documents", [])
        metadatas_db = vs.get("metadatas", [])

    # Build LLM message list
    messages = list(history)  # avoid mutating original list

    # Inject retrieved context (no duplicates)
    if documents:
        for docs, metas in zip(documents, metadatas_db):
            for doc, meta in zip(docs, metas):
                messages.append({
                    "role": "system",
                    "content": doc
                })

    # Add final user query
    messages.append({"role": "user", "content": query})

    # --- SSE GENERATOR ---
    def generate_stream():
        try:
            for token in agent.call_stream(messages):
                # Format for SSE
                yield f"data: {token}\n\n"
        except GeneratorExit:
            # Client disconnected mid-stream
            return
        except Exception as e:
            yield f"data: [ERROR] {str(e)}\n\n"

    # Return streaming response
    return Response(
        stream_with_context(generate_stream()),
        mimetype="text/event-stream",
    )


@app.route('/chat', methods=['POST'])
def chatbot():
    data = request.get_json()

    query = data.get("query")
    n_results = data.get("nResults", 5)
    include = data.get("include", [])
    metadatas = data.get("metadatas")
    use_vectorstore = data.get("useVectorstore", True)  # <--- NEW FLAG

    if not query:
        return jsonify({"message": "QUERY is empty"}), 429

    documents = []
    metadatas_database = []

    # --- OPTIONAL: Only fetch vectorstore when needed ----
    if use_vectorstore:
        vs_data = chroma_db_client.query_collection(
            [query],
            n_results,
            include,
            metadatas
        )
        documents = vs_data.get("documents", [])
        metadatas_database = vs_data.get("metadatas", [])

    # Build message history for LLM
    messages = []

    # Insert retrieved context (if any)
    if documents:
        for docs, metas in zip(documents, metadatas_database):
            for doc, meta in zip(docs, metas):
                messages.append({
                    "role": "system",
                    "content": doc
                })

    # Add the user query at the end
    messages.append({"role": "user", "content": query})

    # Call the LLM agent
    response = agent.call(messages)

    return jsonify({
        "message": response,
        "documents": documents,
        "metadatas": metadatas_database
    }), 200


@app.route('/initialize', methods=['POST'])
def initialize():
    try:
        chroma_db_client.initialize()
        return jsonify({"message": "Collection initialized"}), 200
    except Exception as e:
        print(f"Error initializing collection: {e}")
        return jsonify({"error": "Error initializing collection"}), 500


@app.route('/documents', methods=['POST'])
def add_documents():
    try:
        data = request.get_json()
        documents = data.get('documents', [])
        ids = data.get('ids', [])
        metadatas = data.get('metadatas', None)
        chroma_db_client.add_document(documents, ids, metadatas)
        return jsonify({"message": "Documents added"}), 200
    except Exception as e:
        print(f"Error adding documents: {e}")
        return jsonify({"error": "Error adding documents"}), 500


@app.route('/query', methods=['POST'])
def query_collection():
    try:
        data = request.get_json()
        query_texts = data.get('queryTexts')
        n_results = data.get('nResults', 10)
        include = data.get('include', [])
        metadatas = data.get('metadatas', None)

        results = chroma_db_client.query_collection(
            query_texts=query_texts,
            n_results=n_results,
            include=include,
            metadatas=metadatas
        )

        for t in query_texts[0].split(" "):
            if "metadatas" not in results or not results["metadatas"]:
                continue
            if t.startswith("http") and "youtube.com" in t:
                text = transcript.generateText(t)
                results["metadatas"][0].append({"transcript": text})
            elif t.startswith("http"):
                text = transcript.generateMArkdown(t)
                results["metadatas"][0].append({"web page": text})

        return jsonify(results), 200
    except Exception as e:
        print(f"Error querying collection: {e}")
        return jsonify({"error": "Error querying collection"}), 500


@app.route('/documents', methods=['GET'])
def get_documents():
    try:
        ids = request.args.get('ids', None)
        include = request.args.get('include')
        include_list = include.split(',') if include else [
            "documents", "metadatas"]

        metadatas = request.args.get('metadatas')
        parsed_metadatas = json.loads(metadatas) if metadatas else None
        results = chroma_db_client.get_document(
            ids=ids.split(',') if ids else None,
            include=include_list,
            metadatas=parsed_metadatas
        )
        print("ids : ", ids.split(',') if ids else None, "RESULT : ", results)
        return jsonify(results), 200
    except Exception as e:
        print(f"Error getting documents: {e}")
        return jsonify({"error": "Error getting documents"}), 500


@app.route('/documents', methods=['PUT'])
def update_documents():
    try:
        data = request.get_json()
        ids = data.get('ids')
        documents = data.get('documents')
        chroma_db_client.update_document(ids, documents)
        return jsonify({"message": "Documents updated"}), 200
    except Exception as e:
        print(f"Error updating documents: {e}")
        return jsonify({"error": "Error updating documents"}), 500


@app.route('/documents', methods=['DELETE'])
def delete_documents():
    try:
        data = request.get_json()
        ids = data.get('ids')
        chroma_db_client.delete_document(ids)
        return jsonify({"message": "Documents deleted"}), 200
    except Exception as e:
        print(f"Error deleting documents: {e}")
        return jsonify({"error": "Error deleting documents"}), 500


@app.route('/empty-documents', methods=['DELETE'])
def delete_all_documents():
    try:
        metadatas = request.args.get('metadatas')
        parsed_metadatas = json.loads(metadatas) if metadatas else None
        chroma_db_client.delete_all_documents(parsed_metadatas)
        return jsonify({"message": "success"}), 200
    except Exception as e:
        print(f"Error deleting documents: {e}")
        return jsonify({"error": "Error deleting documents"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
