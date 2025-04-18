# -------------------------------------------------------------------- #
# app.py
# -------------------------------------------------------------------- #
"""
Flask + FMPy mini‑demo
----------------------
• Place Rectifier.fmu in the same folder as this file
• pip install flask fmpy matplotlib
• python app.py
"""

import io, os, tempfile
import matplotlib
matplotlib.use('Agg')  # render plots without a display

from flask import Flask, send_file, render_template_string, redirect, url_for
from fmpy import read_model_description, simulate_fmu
from fmpy.util import plot_result

FMU_FILE = "FirstOrder.fmu"

# -------------------------------------------------------------------- #
# New dynamic simulation
# -------------------------------------------------------------------- #
# fmu_server.py
from flask import request, jsonify
from fmpy import extract
from fmpy.fmi2 import FMU2Slave

app = Flask(__name__)

# Global FMU state
fmu = None
time = 0.0
step_size = 1e-2
vr_input = None
vr_output = None

@app.route('/init')
def init():
    global fmu, time, vr_input, vr_output
    unzipdir = extract('CoupledClutches.fmu')
    model_desc = read_model_description(unzipdir)

    vrs = {v.name: v.valueReference for v in model_desc.modelVariables}
    vr_input = vrs['inputs']
    vr_output = vrs['outputs[4]']

    fmu = FMU2Slave(
        guid=model_desc.guid,
        unzipDirectory=unzipdir,
        modelIdentifier=model_desc.coSimulation.modelIdentifier,
        instanceName='instance1'
    )

    fmu.instantiate()
    fmu.setupExperiment()
    fmu.enterInitializationMode()
    fmu.exitInitializationMode()

    time = 0.0
    return "FMU initialized"

@app.route('/update')
def update_input():
    value = float(request.args.get('input', 0.0))
    fmu.setReal([vr_input], [value])
    return f"Input updated to {value}"

@app.route('/step')
def step():
    global time
    fmu.doStep(currentCommunicationPoint=time, communicationStepSize=step_size)
    time += step_size
    input_val, output_val = fmu.getReal([vr_input, vr_output])
    return jsonify({'time': time, 'input': input_val, 'output': output_val})

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
    <h2>FMPy + Flask demo (Rectifier.fmu)</h2>
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
