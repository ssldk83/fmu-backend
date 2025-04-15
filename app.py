from flask import Flask, jsonify, request
from fmpy import simulate_fmu
import os
import json
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

FMU_FOLDER = os.path.dirname(os.path.abspath(__file__))
RESULT_STORAGE = {}

def run_fmu(filename):
    fmu_path = os.path.join(FMU_FOLDER, filename)
    
    try:
        print(f"📦 Attempting to simulate FMU: {fmu_path}")
        print(f"📁 Files in folder: {os.listdir(FMU_FOLDER)}")

        result = simulate_fmu(fmu_path)
        result_dict = {col: result[col].tolist() for col in result.dtype.names}
        return result_dict

    except Exception as e:
        print(f"❌ FMU simulation failed: {str(e)}")
        return {"error": str(e)}

@app.route('/')
def hello():
    return "🚀 Flask backend is alive!"

@app.route('/simulate/<model_name>', methods=['GET'])
def simulate_model(model_name):
    model_map = {
        "FirstOrder": "FirstOrder.fmu",
        "SecondOrderSystem": "SecondOrderSystem.fmu"
    }

    fmu_file = model_map.get(model_name)
    if not fmu_file:
        return jsonify({"error": "Unknown model name"}), 404

    result = run_fmu(fmu_file)

    if "error" in result:
        return jsonify({"error": result["error"]}), 500

    RESULT_STORAGE['result'] = result
    return jsonify({"variables": list(result.keys())})

@app.route('/data', methods=['GET'])
def get_data():
    x = request.args.get('x')
    y = request.args.get('y')
    result = RESULT_STORAGE.get('result')

    if not result:
        return jsonify({"error": "No simulation result cached yet"}), 400
    if x not in result or y not in result:
        return jsonify({"error": f"Invalid variable(s): {x}, {y}"}), 400

    return jsonify({
        "x": result[x],
        "y": result[y]
    })

@app.route('/models')
def list_models():
    return jsonify(["FirstOrder", "SecondOrderSystem"])

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
