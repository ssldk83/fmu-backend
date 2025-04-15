from flask import Flask, jsonify, request
from fmpy import simulate_fmu
from fmpy.util import read_model_description
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

@app.route('/simulate/<model_name>', methods=['GET'])
def simulate_model(model_name):
    fmu_file = f"{model_name}.fmu"
    if not os.path.exists(os.path.join(FMU_FOLDER, fmu_file)):
        return jsonify({"error": "FMU not found"}), 404
    
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

if __name__ == '__main__':
    app.run(debug=True)
