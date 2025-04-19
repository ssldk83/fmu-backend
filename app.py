import dash
from dash import dcc, html, Output, Input, State
import plotly.graph_objs as go
from fmpy import extract, read_model_description, instantiate_fmu
import threading
import numpy as np
import time
import os

app = dash.Dash(__name__)
server = app.server

FMU_PATH = "CoupledClutches.fmu"
STEP_SIZE = 1e-3
STOP_TIME = 60.0  # increase simulation time for continuous feel

sim_data = {
    "time": [],
    "output": [],
    "param_value": 0.0,
    "running": False
}

def simulate_realtime():
    print("Starting simulation...")
    try:
        unzipdir = extract(FMU_PATH)
        model_description = read_model_description(unzipdir)
        fmu = instantiate_fmu(unzipdir=unzipdir, model_description=model_description, fmi_type='CoSimulation')

        fmu.setupExperiment()
        fmu.enterInitializationMode()
        fmu.exitInitializationMode()

        time_val = 0.0
        vr_inputs = [v.valueReference for v in model_description.modelVariables if v.name == "inputs"]
        vr_outputs = [v.valueReference for v in model_description.modelVariables if v.name == "outputs[4]"]

        if not vr_inputs or not vr_outputs:
            print("Variable references not found. Aborting.")
            return

        vr_inputs = vr_inputs[0]
        vr_outputs = vr_outputs[0]

        sim_data["time"] = []
        sim_data["output"] = []
        sim_data["running"] = True

        while sim_data["running"]:
            fmu.setReal([vr_inputs], [sim_data["param_value"]])
            fmu.doStep(currentCommunicationPoint=time_val, communicationStepSize=STEP_SIZE)
            y = fmu.getReal([vr_outputs])[0]

            sim_data["time"].append(time_val)
            sim_data["output"].append(y)

            time_val += STEP_SIZE
            time.sleep(STEP_SIZE)

            if time_val > STOP_TIME:
                time_val = 0.0
                sim_data["time"] = []
                sim_data["output"] = []

        fmu.terminate()
        fmu.freeInstance()
        os.system(f"rm -rf {unzipdir}")
        print("Simulation completed.")
    except Exception as e:
        print(f"Simulation error: {e}")
        sim_data["running"] = False

if not sim_data["running"]:
    thread = threading.Thread(target=simulate_realtime)
    thread.start()

app.layout = html.Div([
    html.H2("Coupled Clutches Simulation (Dash)"),
    dcc.Slider(
        id='param-slider',
        min=0, max=1, step=0.01, value=0.0,
        marks={i/10: f"{i/10}" for i in range(0, 11)}
    ),
    html.Div(id='slider-output'),
    dcc.Graph(id='live-graph'),
    dcc.Interval(
        id='interval-component',
        interval=500,  # in milliseconds
        n_intervals=0
    )
])

@app.callback(
    Output('slider-output', 'children'),
    Input('param-slider', 'value')
)
def update_param(value):
    sim_data["param_value"] = float(value)
    return f"Input Value: {value:.2f}"

@app.callback(
    Output('live-graph', 'figure'),
    Input('interval-component', 'n_intervals')
)
def update_graph(n):
    if not sim_data["time"]:
        t = np.linspace(0, 10, 200)
        y = np.sin(t)
    else:
        t = sim_data["time"]
        y = sim_data["output"]
    return {
        'data': [go.Scatter(x=t, y=y, mode='lines', line=dict(color='blue'))],
        'layout': go.Layout(title='Output [4]', xaxis=dict(title='Time (s)'), yaxis=dict(title='Output'), uirevision='true')
    }

if __name__ == '__main__':
    app.run_server(debug=True, port=5000)
