# app.py
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

FMU_FILE = "Rectifier.fmu"

app = Flask(__name__)

# -------------------------------------------------------------------- #
# 1) dump(fmu)  ->  /dump
# -------------------------------------------------------------------- #
@app.route("/dump")
def dump_fmu():
    md = read_model_description(FMU_FILE)

    info = f"""
Model Info
-----------
FMI Version       {md.fmiVersion}
Model Name        {md.modelName}
Description       {md.description or ''}
Platforms         {", ".join(md.coSimulation.modelIdentifier)}
Continuous States {md.numberOfContinuousStates}
Event Indicators  {md.numberOfEventIndicators}
Generation Tool   {md.generationTool}
Generation Date   {md.generationDateAndTime}

Default Experiment
------------------
Stop Time         {md.defaultExperiment.stopTime}
Step Size         {md.defaultExperiment.stepSize}
"""

    # list a few variables marked as outputs
    outputs = [
        v for v in md.modelVariables if v.causality == "output"
    ][:10]  # first ten for brevity

    for v in outputs:
        info += f"\n{v.name:20}  output  {v.start:>12}  {v.unit or ''}  {v.description or ''}"

    return f"<pre>{info}</pre>"


# -------------------------------------------------------------------- #
# 2) simulate_fmu(fmu) + 3) plot_result(result)  ->  /plot
# -------------------------------------------------------------------- #
@app.route("/plot")
def plot():
    # -- simulate the FMU ------------------------------------------------
    result = simulate_fmu(FMU_FILE)

    # -- create a matplotlib Figure with FMPy's helper -------------------
    fig = plot_result(result)

    # -- stream the plot to the browser as PNG ---------------------------
    png_io = io.BytesIO()
    fig.savefig(png_io, format="png", bbox_inches="tight", dpi=150)
    png_io.seek(0)
    return send_file(png_io, mimetype="image/png")


# optional helper route so users land somewhere nice
@app.route("/")
def index():
    html = """
    <h2>FMPy + Flask demo (Rectifier.fmu)</h2>
    <ul>
      <li><a href="/dump">/dump</a> &nbsp;→ show model information (like <code>dump(fmu)</code>)</li>
      <li><a href="/plot">/plot</a> &nbsp;→ run simulation &amp; display plot</li>
    </ul>
    """
    return render_template_string(html)


# -------------------------------------------------------------------- #
# Run the Flask server (Render/Heroku friendly)
# -------------------------------------------------------------------- #
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render sets PORT env‑var
    app.run(host="0.0.0.0", port=port, debug=True)
