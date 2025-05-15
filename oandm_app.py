from flask import Flask, request, send_file, render_template
from werkzeug.utils import secure_filename
from docx import Document
import os
import shutil
import uuid

app = Flask(__name__)
UPLOAD_FOLDER = "app/uploads"
GENERATED_FOLDER = "app/generated"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(GENERATED_FOLDER, exist_ok=True)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload_files():
    folder_id = str(uuid.uuid4())
    folder_path = os.path.join(UPLOAD_FOLDER, folder_id)
    os.makedirs(folder_path, exist_ok=True)

    files = request.files.getlist("files[]")
    for file in files:
        filename = secure_filename(file.filename)
        subfolder = os.path.dirname(filename)
        full_path = os.path.join(folder_path, filename)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        file.save(full_path)

    # Generate docx
    doc = Document()
    doc.add_heading("Operations & Maintenance Manual", 0)

    for root, dirs, files in os.walk(folder_path):
        if files:
            section_title = os.path.basename(root)
            doc.add_page_break()
            doc.add_heading(f"Equipment: {section_title}", level=1)
            doc.add_paragraph("Included documents:")
            for f in files:
                doc.add_paragraph(f"• {f}")

    output_path = os.path.join(GENERATED_FOLDER, f"{folder_id}.docx")
    doc.save(output_path)

    return send_file(output_path, as_attachment=True)
