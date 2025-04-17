from flask import Flask, jsonify, request
from flask_cors import CORS
from fmpy import read_model_description, simulate_fmu
import functools, os, logging

app = Flask(__name__)
CORS(app)
app.logger.setLevel(logging.INFO)

# --------------------------------------------------------------------------
# simulate each FMU only once per container life‑time and cache the result
# --------------------------------------------------------------------------
@functools.lru_cache(maxsize=None)
def _simulate_once(model_name: str, *, stop_time=10.0):
    fmu_file = f"{model_name}.fmu"
    if not os.path.isfile(fmu_file):
        raise FileNotFoundError(f"FMU {fmu_file} not found")

    app.logger.info("First‑time simulation of %s (stop=%s)", model_name, stop_time)
    result = simulate_fmu(fmu_file, start_time=0.0, stop_time=stop_time)
    return result, set(result.dtype.names)


# --------------------------------------------------------------------------
# Routes
# --------------------------------------------------------------------------
@app.route("/simulate/<model>")
def simulate(model):
    fmu_file = f"{model}.fmu"
    if not os.path.isfile(fmu_file):
        return jsonify(error="FMU not found"), 404

    md = read_model_description(fmu_file)
    return jsonify(variables=[v.name for v in md.modelVariables])


@app.route("/data")
def get_data():
    model = request.args.get("model", "FirstOrder")
    x     = request.args.get("x")
    y     = request.args.get("y")

    if not x or not y:
        return jsonify(error="x and y query parameters are required"), 400

    try:
        result, names = _simulate_once(model)
    except FileNotFoundError:
        return jsonify(error="FMU not found"), 404
    except Exception as exc:  # compile or runtime failure
        app.logger.exception("FMU simulation failed")
        return jsonify(error=str(exc)), 500

    if x not in names or y not in names:
        return jsonify(error=f"Variables {x} or {y} not found"), 400

    return jsonify(x=result[x].tolist(), y=result[y].tolist())


# --------------------------------------------------------------------------
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
