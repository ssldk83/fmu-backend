from flask import Flask, jsonify, request
from flask_cors import CORS
import fmpy
from fmpy import simulate_fmu
from fmpy.util import read_model_description
import os

app = Flask(__name__)
CORS(app)

FMU_PATH = "output/FirstOrder.fmu"  # Or load dynamically

@app.route("/simulate/<model_name>")
def simulate(model_name):
    fmu_file = f"output/{model_name}.fmu"
    if not os.path.isfile(fmu_file):
        return jsonify({"error": "FMU not found"}), 404

    model_description = read_model_description(fmu_file)
    variables = [v.name for v in model_description.modelVariables]
    return jsonify({"variables": variables})

@app.route("/data")
def get_data():
    x = request.args.get("x")
    y = request.args.get("y")

    # Simulate
    result = simulate_fmu(FMU_PATH, start_time=0.0, stop_time=10.0)
    if x not in result.dtype.names or y not in result.dtype.names:
        return jsonify({"error": "Invalid variable names"}), 400

    return jsonify({
        "x": result[x].tolist(),
        "y": result[y].tolist()
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
