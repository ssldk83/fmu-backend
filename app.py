from flask import Flask, jsonify, request
from fmpy import simulate_fmu
import os
import tempfile
import json

app = Flask(__name__)

FMU_FOLDER = os.path.dirname(os.path.abspath(__file__))
RESULT_STORAGE = {}  # for simplicity, cache results in memory

def run_fmu(filename):
    fmu_path = os.path.join(FMU_FOLDER, filename)
    
    # Simulate and store the result
    result = simulate_fmu(fmu_path)
    result_dict = {col: result[col].tolist() for col in result.dtype.names}
    
    return result_dict

@app.route('/')
def hello():
    return "🚀 Flask backend is alive!"
    
@app.route('/simulate/<model_name>', methods=['GET'])
def simulate_model(model_name):
    if model_name == "FirstOrder":
        fmu_file = "FirstOrder.fmu"
    elif model_name == "SecondOrderSystem":
        fmu_file = "SecondOrderSystem.fmu"
    else:
        return jsonify({"error": "unknown model"}), 404
        
    result = run_fmu(fmu_file)
    RESULT_STORAGE['result'] = result  # overwrite for simplicity
    return jsonify({"variables": list(result.keys())})

@app.route('/data', methods=['GET'])
def get_data():
    x = request.args.get('x')
    y = request.args.get('y')
    result = RESULT_STORAGE.get('result')
    
    if not result or x not in result or y not in result:
        return jsonify({"error": "Missing or invalid data"}), 400

    return jsonify({
        "x": result[x],
        "y": result[y]
    })

@app.route('/models')
def list_models():
    return jsonify(["FirstOrder", "SecondOrderSystem"])

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Render sets PORT automatically
    app.run(host="0.0.0.0", port=port)
