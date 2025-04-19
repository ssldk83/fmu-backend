# -------------------------------------------------------------------- #
# app.py
# -------------------------------------------------------------------- #

from flask import Flask, send_file, render_template_string, redirect, url_for, request, jsonify
from fmpy import read_model_description, simulate_fmu, instantiate_fmu, extract
from fmpy.util import plot_result
from fmpy.fmi2 import FMU2Slave
from flask_cors import CORS

import threading
import time
import numpy as np
import os

import io, tempfile
import matplotlib
matplotlib.use('Agg')  # render plots without a display

# -------------------------------------------------------------------- #
# New dynamic simulation
# -------------------------------------------------------------------- #

FMU_FILE = "RealtimeOscillator.fmu"
app = Flask(__name__)
CORS(app)

# Global FMU state
fmu = None
time = 0.0
step_size = 1e-2
vr_input = None
vr_output = None


FMU_PATH = "RealtimeOscillator.fmu"  # Replace with your FMU
STEP_SIZE = 1e-3
STOP_TIME = 2.0

# Global simulation state
sim_data = {
    "time": [],
    "output": [],
    "param_value": 0.0,
    "running": False
}

def simulate_realtime():
    unzipdir = extract(FMU_PATH)
    model_description = read_model_description(unzipdir)
    fmu = instantiate_fmu(unzipdir=unzipdir, model_description=model_description, fmi_type='CoSimulation')

    fmu.setupExperiment()
    fmu.enterInitializationMode()
    fmu.exitInitializationMode()

    time_val = 0.0
    vr_inputs = [v.valueReference for v in model_description.modelVariables if v.name == "inputs"][0]
    vr_outputs = [v.valueReference for v in model_description.modelVariables if v.name == "outputs[4]"][0]

    sim_data["time"] = []
    sim_data["output"] = []
    sim_data["running"] = True

    while time_val < STOP_TIME and sim_data["running"]:
        # Allow real-time input change
        fmu.setReal([vr_inputs], [sim_data["param_value"]])

        fmu.doStep(currentCommunicationPoint=time_val, communicationStepSize=STEP_SIZE)
        y = fmu.getReal([vr_outputs])[0]

        sim_data["time"].append(time_val)
        sim_data["output"].append(y)

        time_val += STEP_SIZE
        time.sleep(STEP_SIZE)  # Simulate real-time

    fmu.terminate()
    fmu.freeInstance()
    os.system(f"rm -rf {unzipdir}")

@app.route("/simulate", methods=["POST"])
def start_sim():
    print("Simulation requested...")
    if not sim_data["running"]:
        thread = threading.Thread(target=simulate_realtime)
        thread.start()
        print("Simulation thread started.")
    else:
        print("Simulation already running.")
    return jsonify({"status": "simulation started"})

@app.route("/update", methods=["POST"])
def update_param():
    new_val = request.json.get("value")
    sim_data["param_value"] = float(new_val)
    return jsonify({"status": "updated", "new_value": sim_data["param_value"]})

@app.route("/data", methods=["GET"])
def get_data():
    return jsonify({"time": sim_data["time"], "output": sim_data["output"]})

# -------------------------------------------------------------------- #
# 1) dump(fmu)  ->  /dump
# -------------------------------------------------------------------- #
@app.route("/dump")
def dump_fmu():
    md = read_model_description(FMU_FILE)

    # ---------- header info ----------
    lines = [
        "Model Info",
        "-----------",
        f"FMI Version       {md.fmiVersion}",
        f"Model Name        {md.modelName}",
        f"Description       {md.description or ''}",
        f"Continuous States {md.numberOfContinuousStates}",
        f"Event Indicators  {md.numberOfEventIndicators}",
        "",
        "Default Experiment",
        "------------------",
        f"Stop Time         {getattr(md.defaultExperiment, 'stopTime', '')}",
        f"Step Size         {getattr(md.defaultExperiment, 'stepSize', '')}",
        "",
        "Variables (first 20 outputs)",
        "Name                 Causality   Start Value    Unit   Description",
        "-------------------- ---------- -------------- ------ ---------------------------",
    ]

    # ---------- list first 20 output variables ----------
    outputs = [v for v in md.modelVariables if v.causality == "output"][:20]
    for v in outputs:
        start_val = "" if v.start is None else v.start
        unit      = "" if v.unit  is None else v.unit
        desc      = "" if v.description is None else v.description
        lines.append(f"{v.name:20}  output   {str(start_val):>12}  {unit:6} {desc}")

    return "<pre>" + "\n".join(lines) + "</pre>"


# -------------------------------------------------------------------- #
# 2) simulate_fmu(fmu) + 3) plot_result(result)  ->  /plot
# -------------------------------------------------------------------- #
@app.route("/chart")
def chart():
    result = simulate_fmu(FMU_FILE)

    time = result['time'].tolist()
    x = result['x'].tolist()

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Chart.js FMU Plot</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    </head>
    <body>
        <h2 style="text-align:center;">FMU Simulation Result: x vs time</h2>
        <canvas id="fmuChart" width="800" height="400"></canvas>
        <script>
            const ctx = document.getElementById('fmuChart').getContext('2d');
            const chart = new Chart(ctx, {{
                type: 'line',
                data: {{
                    labels: {time},
                    datasets: [{{
                        label: 'x',
                        data: {x},
                        borderColor: 'green',
                        fill: false,
                        tension: 0.3
                    }}]
                }},
                options: {{
                    responsive: true,
                    scales: {{
                        x: {{
                            title: {{
                                display: true,
                                text: 'time [s]'
                            }}
                        }},
                        y: {{
                            title: {{
                                display: true,
                                text: 'x'
                            }}
                        }}
                    }}
                }}
            }});
        </script>
    </body>
    </html>
    """
    return html



# -------------------------------------------------------------------- #
# optional helper route so users land somewhere nice
# -------------------------------------------------------------------- #
@app.route("/")
def index():
    html = """
    <h2>FMPy + Flask demo (FirtOrder.fmu)</h2>
    <ul>
      <li><a href="/dump">/dump</a> &nbsp;→ show model information (like <code>dump(fmu)</code>)</li>
      <li><a href="/chart">/chart</a> &nbsp;→ run simulation &amp; display plot</li>
      <li><a href="/variables">/variables</a> &nbsp;→ run simulation &amp; display plot</li>
    </ul>
    """
    return render_template_string(html)

@app.route("/variables")
def show_vars():
    result = simulate_fmu(FMU_FILE)
    return "<pre>" + "\n".join(result.dtype.names) + "</pre>"


# -------------------------------------------------------------------- #
# Run the Flask server (Render/Heroku friendly)
# -------------------------------------------------------------------- #
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render sets PORT env‑var
    app.run(host="0.0.0.0", port=port, debug=True)
