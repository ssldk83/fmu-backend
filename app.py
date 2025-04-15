from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import fmpy
from fmpy import simulate_fmu, read_model_description, extract
import numpy as np
import matplotlib.pyplot as plt
import io
import traceback

app = Flask(__name__)
CORS(app)

FMU_FILE = 'FirstOrder.fmu'
SIM_TIME = 10
last_sim_data = {}

@app.route('/simulate', methods=['POST'])
def simulate():
    global last_sim_data
    try:
        model_description = read_model_description(FMU_FILE, validate=False)
        unzipdir = extract(FMU_FILE)
        result = simulate_fmu(filename=unzipdir, stop_time=SIM_TIME, validate=False)

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

@app.route('/plot', methods=['GET'])
def plot_png():
    x = request.args.get('x', 'time')
    y = request.args.get('y')

    if not last_sim_data:
        return jsonify({"error": "No simulation data found."}), 400

    if not y:
        y = next((v for v in last_sim_data if v != 'time'), None)

    if not x or not y or x not in last_sim_data or y not in last_sim_data:
        return jsonify({"error": f"Invalid variables: {x}, {y}"}), 400

    fig, ax = plt.subplots()
    ax.plot(last_sim_data[x], last_sim_data[y])
    ax.set_xlabel(x)
    ax.set_ylabel(y)
    ax.set_title(f"{y} vs. {x}")

    img = io.BytesIO()
    fig.savefig(img, format='png')
    img.seek(0)
    plt.close(fig)

    return send_file(img, mimetype='image/png')

@app.route('/debug', methods=['GET'])
def debug():
    return jsonify({"fmu_file": FMU_FILE, "status": "Ready"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
