from flask import Flask, request, jsonify
from flask_cors import CORS
from chromadb.config import Settings
from werkzeug.utils import secure_filename
import os
from PyPDF2 import PdfReader
import io

app = Flask(__name__)
CORS(app)
port = 3001

@app.route("/upload/", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return "No file uploaded.", 400

    file = request.files["file"]
    if file.filename == "":
        return "No file selected.", 400

    if file:
        try:
            pdf_reader = PdfReader(io.BytesIO(file.read()))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()

            return jsonify({"text": text}), 200
        except Exception as e:
            return "Error processing the PDF file.", 500

if __name__ == "__main__":
    app.run(port=port, debug=True)

