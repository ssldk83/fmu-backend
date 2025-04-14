from flask import Flask, request, jsonify
from flask_cors import CORS
import fmpy
from fmpy import simulate_fmu, read_model_description, extract
import numpy as np
import traceback

app = Flask(__name__)
CORS(app)

FMU_FILE = 'SecondOrderSystem.fmu'
SIM_TIME = 10
last_sim_data = {}

@app.route('/simulate', methods=['POST'])
def simulate():
    global last_sim_data
    try:
        # Extract FMU and disable unit validation
        model_description = read_model_description(FMU_FILE, validate=False)
        unzipdir = extract(FMU_FILE)  # extract returns folder path
        result = simulate_fmu(filename=unzipdir, stop_time=SIM_TIME)
        
        last_sim_data = {name: result[name].tolist() for name in result.dtype.names}
        return jsonify({
            "message": "Simulation successful.",
            "variables_found": list(last_sim_data.keys())
        })
    except Exception as e:
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500


@app.route('/variables', methods=['GET'])
def variables():
    return jsonify({"variables": list(last_sim_data.keys()) if last_sim_data else []})

@app.route('/data', methods=['GET'])
def data():
    x = request.args.get('x')
    y = request.args.get('y')

    if not x or not y or x not in last_sim_data or y not in last_sim_data:
        return jsonify({"error": "Invalid variables."}), 400

    return jsonify({
        "x": last_sim_data[x],
        "y": last_sim_data[y],
        "x_label": x,
        "y_label": y
    })

@app.route('/debug', methods=['GET'])
def debug():
    return jsonify({"fmu_file": FMU_FILE, "status": "Ready"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
