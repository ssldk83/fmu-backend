import os, functools
from flask import Flask, jsonify, request
from fmpy import read_model_description, simulate_fmu
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# simple in‑memory cache {model_name: (result, dtype_names)}
_cache = {}

def run_once(model):
    """simulate a model only once per container life‑time"""
    if model in _cache:
        return _cache[model]
    result = simulate_fmu(f"{model}.fmu", start_time=0.0, stop_time=10.0)
    _cache[model] = (result, set(result.dtype.names))
    return _cache[model]

@app.route("/simulate/<model>")
def simulate(model):
    fmu = f"{model}.fmu"
    if not os.path.isfile(fmu):
        return jsonify(error="FMU not found"), 404
    md = read_model_description(fmu)
    return jsonify(variables=[v.name for v in md.modelVariables])

@app.route("/data")
def get_data():
    model  = request.args.get("model", "FirstOrder")   # optional ?model=
    x = request.args.get("x")
    y = request.args.get("y")

    if not x or not y:
        return jsonify(error="x and y required"), 400

    try:
        result, names = run_once(model)
    except FileNotFoundError:
        return jsonify(error="FMU not found"), 404

    if x not in names or y not in names:
        return jsonify(error="Invalid variable names"), 400

    return jsonify(x=result[x].tolist(), y=result[y].tolist())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
