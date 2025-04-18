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
