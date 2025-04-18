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
import plotly.graph_objs as go
import plotly.io as pio

@app.route("/plot")
def plot():
    try:
        result = simulate_fmu(FMU_FILE)
        time = result['time']
        a = result['a']
    except Exception as e:
        return f"<pre>Simulation failed: {e}</pre>"

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=time, y=a, mode='lines', name='a'))
    fig.update_layout(
        title="FMU Simulation Result",
        xaxis_title="time [s]",
        yaxis_title="a",
        margin=dict(l=40, r=40, t=40, b=40)
    )

    return pio.to_html(fig, full_html=True)

@app.route('/chart')
def chart():
    result = simulate_fmu(FMU_FILE)
    time = result['time'].tolist()
    a = result['a'].tolist()

    # Render the HTML with embedded Chart.js and data
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Chart.js FMU Plot</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    </head>
    <body>
        <h2 style="text-align:center;">FMU Simulation Result (Chart.js)</h2>
        <canvas id="fmuChart" width="800" height="400"></canvas>
        <script>
            const ctx = document.getElementById('fmuChart').getContext('2d');
            const chart = new Chart(ctx, {{
                type: 'line',
                data: {{
                    labels: {time},
                    datasets: [{{
                        label: 'a vs time',
                        data: {a},
                        borderColor: 'blue',
                        fill: false,
                        tension: 0.2
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
                                text: 'a'
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


# optional helper route so users land somewhere nice
@app.route("/")
def index():
    html = """
    <h2>FMPy + Flask demo (Rectifier.fmu)</h2>
    <ul>
      <li><a href="/dump">/dump</a> &nbsp;→ show model information (like <code>dump(fmu)</code>)</li>
      <li><a href="/plot">/plot</a> &nbsp;→ run simulation &amp; display plot</li>
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
