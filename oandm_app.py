# oandm_app.py

from flask import Blueprint, request, jsonify
import openai
import os

oandm_bp = Blueprint('oandm', __name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

@oandm_bp.route('/generate', methods=['POST'])
def generate_om_manual():
    data = request.json
    equipment_type = data.get("equipment_type", "")
    details = data.get("details", "")

    prompt = f"""Write an Operations & Maintenance manual section for a {equipment_type}.
Include purpose, normal operating procedure, shutdown, maintenance, and spare parts.
Details: {details}"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert in technical documentation for process plants."},
                {"role": "user", "content": prompt}
            ]
        )
        return jsonify({"content": response.choices[0].message["content"]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
