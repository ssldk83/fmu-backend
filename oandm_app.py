from flask import Blueprint, request, jsonify
from openai import OpenAI
import os
import traceback

oandm_bp = Blueprint('oandm', __name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@oandm_bp.route("/ping", methods=["GET"])
def ping():
    return jsonify({"message": "O&M backend is alive."})

@oandm_bp.route("/generate", methods=["POST"])
def generate_om_manual():
    try:
        data = request.json
        equipment_name = data.get("equipment_name", "Unknown Equipment")
        filenames = data.get("filenames", [])

        prompt = f"""You are an expert in industrial O&M documentation.

Write a professional Operations & Maintenance manual section for: {equipment_name}
Assume the following documents exist in the folder: {filenames}

Include:
- Description / purpose
- Installation (if applicable)
- Startup procedure
- Normal operation
- Shutdown procedure
- Maintenance intervals
- Spare parts

Respond in clear, structured text with headings. Avoid placeholders like "insert here".
"""

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a senior process engineer."},
                {"role": "user", "content": prompt}
            ]
        )

        content = response.choices[0].message.content
        return jsonify({"content": content})

    except Exception as e:
        print("🔥 Error in /generate route:")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
