from flask import Blueprint, request, jsonify
import os
import traceback
from openai import OpenAI

oandm_bp = Blueprint('oandm', __name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@oandm_bp.route('/ping', methods=['GET'])
def ping():
    return jsonify({"message": "O&M backend is alive."})

@oandm_bp.route('/generate', methods=['POST'])
def generate_om_manual():
    data = request.json
    equipment_type = data.get("equipment_type", "")
    details = data.get("details", "")

    prompt = f"""Write an Operations & Maintenance manual section for a {equipment_type}.
Include purpose, normal operation, shutdown, maintenance interval, and spare parts list.
Details: {details}"""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert in technical documentation for engineers."},
                {"role": "user", "content": prompt}
            ]
        )
        result = response.choices[0].message.content
        return jsonify({"content": result})

    except Exception as e:
        print("🔥 OpenAI error:")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
