# firstorder_app.py (standalone Dash app for FirstOrder.fmu, no inputs)
import dash
from dash import dcc, html
import plotly.graph_objs as go
from fmpy import simulate_fmu
import os


def init_firstorder(server):
    app = dash.Dash(__name__, server=server, url_base_pathname='/firstorder/', suppress_callback_exceptions=True)

    FMU_PATH = "FirstOrder.fmu"

    if os.path.exists(FMU_PATH):
        try:
            result = simulate_fmu(FMU_PATH, start_time=0.0, stop_time=8.0, step_size=0.01, output=['x'])
            time = result['time']
            x = result['x']
        except Exception as e:
            print(f"Simulation failed: {e}")
            time = [0]
            x = [0]
    else:
        print("FMU not found!")
        time = [0]
        x = [0]


    app.layout = html.Div([
        html.H2("FirstOrder FMU Simulation"),
        dcc.Graph(
            id="fmu-plot",
            figure=go.Figure(
                data=[go.Scatter(x=time, y=x, mode='lines', name='x(t)')],
                layout=go.Layout(
                    title='x vs Time',
                    xaxis_title='Time [s]',
                    yaxis_title='x',
                    margin=dict(l=40, r=20, t=40, b=40)
                )
            ),
            config={"displayModeBar": False}
        )
    ], className="dash-container")
