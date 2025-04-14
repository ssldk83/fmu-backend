from flask import Flask, request, jsonify
from flask_cors import CORS
import fmpy
import numpy as np
import traceback

app = Flask(__name__)
CORS(app)

FMU_FILENAME = 'FirstOrder.fmu'  # Ensure this file is in your repo and deployed with the app
SIMULATION_STOP_TIME = 10

last_sim_data = {}

@app.route('/simulate', methods=['POST'])
def simulate():
    global last_sim_data
    try:
        print("Simulating FMU...")
        result = fmpy.simulate_fmu(FMU_FILENAME, stop_time=SIMULATION_STOP_TIME)
        print("Simulation complete.")

        last_sim_data = {key: result[key].tolist() for key in result.dtype.names}
        print("Variables:", list(last_sim_data.keys()))

        return jsonify({
            "message": "Simulation successful.",
            "variables_found": list(last_sim_data.keys())
        })

    except Exception as e:
        import traceback
        print("Simulation error:", traceback.format_exc())
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500


@app.route('/variables', methods=['GET'])
def variables():
    if not last_sim_data:
        return jsonify({"variables": []})
    return jsonify({"variables": list(last_sim_data.keys())})


@app.route('/data', methods=['GET'])
def data():
    x_var = request.args.get('x')
    y_var = request.args.get('y')

    if not x_var or not y_var or x_var not in last_sim_data or y_var not in last_sim_data:
        return jsonify({"error": "Invalid variables."}), 400

    return jsonify({
        "x": last_sim_data[x_var],
        "y": last_sim_data[y_var],
        "x_label": x_var,
        "y_label": y_var
    })


@app.route('/debug', methods=['GET'])
def debug():
    return jsonify({"fmu_file": FMU_FILENAME, "status": "Ready"})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
