import os
import uuid
import traceback
from flask import Blueprint, request, jsonify, send_file
from werkzeug.utils import secure_filename
from openai import OpenAI
from docx import Document

UPLOAD_FOLDER = "app/uploads"
GENERATED_FOLDER = "app/generated"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(GENERATED_FOLDER, exist_ok=True)

@oandm_bp.route("/upload", methods=["POST"])
def upload_files():
    folder_id = str(uuid.uuid4())
    folder_path = os.path.join(UPLOAD_FOLDER, folder_id)
    os.makedirs(folder_path, exist_ok=True)

    files = request.files.getlist("files[]")
    for file in files:
        filename = secure_filename(file.filename)
        full_path = os.path.join(folder_path, filename)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        file.save(full_path)

    # Generate .docx
    doc = Document()
    doc.add_heading("Operations & Maintenance Manual", 0)

    for root, dirs, file_list in os.walk(folder_path):
        if file_list:
            section = os.path.basename(root)
            doc.add_page_break()
            doc.add_heading(f"Equipment: {section}", level=1)
            doc.add_paragraph("Files included:")
            for f in file_list:
                doc.add_paragraph(f"• {f}")

    output_path = os.path.join(GENERATED_FOLDER, f"{folder_id}.docx")
    doc.save(output_path)
    return send_file(output_path, as_attachment=True)
