import dash
from dash import dcc, html, Input, Output
import plotly.graph_objs as go
import threading
import numpy as np
import time
import os
from fmpy import extract, read_model_description, instantiate_fmu

def init_realtimeoscillator(server):
    app = dash.Dash(__name__, server=server, url_base_pathname='/realtimeoscillator/', suppress_callback_exceptions=True)

    FMU_PATH = "RealtimeOscillator.fmu"
    STEP_SIZE = 1e-3
    STOP_TIME = 60.0

    sim_data = {
        "time": [],
        "output": [],
        "running": False
    }

    def simulate_realtime():
        try:
            unzipdir = extract(FMU_PATH)
            model_description = read_model_description(unzipdir)
            print("Variables in the FMU:")
            for v in model_description.modelVariables:
                print(f"{v.name} ({v.causality})")

            if model_description.coSimulation is not None:
                fmi_type = 'CoSimulation'
            elif model_description.modelExchange is not None:
                fmi_type = 'ModelExchange'
            else:
                raise Exception("FMU does not support CoSimulation or ModelExchange")

            fmu = instantiate_fmu(unzipdir=unzipdir, model_description=model_description, fmi_type=fmi_type)
            fmu.setupExperiment()
            fmu.enterInitializationMode()
            fmu.exitInitializationMode()

            time_val = 0.0
            outputs = [v.valueReference for v in model_description.modelVariables if v.causality == "output"]

            if not outputs:
                print("Output variable not found. Aborting.")
                return

            vr_output = outputs[0]

            sim_data["time"].clear()
            sim_data["output"].clear()
            sim_data["running"] = True

            while sim_data["running"]:
                fmu.doStep(currentCommunicationPoint=time_val, communicationStepSize=STEP_SIZE)
                y = fmu.getReal([vr_output])[0]

                sim_data["time"].append(time_val)
                sim_data["output"].append(y)

                time_val += STEP_SIZE
                time.sleep(STEP_SIZE)

                if time_val > STOP_TIME:
                    time_val = 0.0
                    sim_data["time"].clear()
                    sim_data["output"].clear()

            fmu.terminate()
            fmu.freeInstance()
            os.system(f"rm -rf {unzipdir}")
        except Exception as e:
            print(f"Simulation error: {e}")
            sim_data["running"] = False

    if not sim_data["running"]:
        thread = threading.Thread(target=simulate_realtime)
        thread.start()

    app.layout = html.Div([
        html.H2("Realtime Oscillator Simulation"),
        dcc.Graph(id='live-graph', config={"displayModeBar": False}),
        dcc.Interval(id='interval-component', interval=500, n_intervals=0)
    ])

    @app.callback(Output('live-graph', 'figure'), Input('interval-component', 'n_intervals'))
    def update_graph(n):
        t = sim_data["time"] if sim_data["time"] else np.linspace(0, 10, 200)
        y = sim_data["output"] if sim_data["output"] else np.sin(t)
        return go.Figure(data=[go.Scatter(x=t, y=y, mode='lines')],
                         layout=go.Layout(title='Output', xaxis_title='Time (s)', yaxis_title='Output'))
