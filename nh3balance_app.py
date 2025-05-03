# nh3balance_app.py

from flask import Blueprint
import dash
from dash import html, dcc, Input, Output
import locale

locale.setlocale(locale.LC_ALL, '')

# Define the Flask blueprint
nh3balance_bp = Blueprint('nh3balance', __name__, url_prefix='/nh3balance')


def create_dash_app(server):
    app = dash.Dash(
        __name__,
        server=server,
        url_base_pathname='/nh3balance/',
        suppress_callback_exceptions=True
    )

    def input_group(label, input_id, unit, disabled=False, value=0):
        return html.Div([
            html.Label(label, className="form-label"),
            html.Div([
                dcc.Input(id=input_id, type='number', value=value, step=10, disabled=disabled, className="form-control"),
                html.Span(unit, className="input-group-text")
            ], className="input-group mb-3")
        ])

    app.layout = html.Div([
        html.Div([
            html.Div([
                input_group("Power to Electrolysis Plant", 'mw_elect', "MW", disabled=False, value=1000),
                input_group("Produced Dry Hydrogen", 'prod_h2', "Nm³/h", disabled=True),
                input_group("Produced Oxygen", 'prod_o2', "Nm³/h", disabled=True),
                input_group("Required Nitrogen for Haber Bosch Process", 'n2_hb', "Nm³/h", disabled=True),
                input_group("Produced Liquid Ammonia", 'prod_nh3', "t/h", disabled=True),
                input_group("Tail Gas to Flare", 'tail_nh3', "Nm³/h dry", disabled=True),
                input_group("Required Water for Water Electrolysis", 'water_h2', "t/h", disabled=True),
                input_group("Required Cooling Water for Water Electrolysis", 'cooling_h2', "t/h", disabled=True)
            ], className="card p-4 shadow-sm")
        ], className="container")
    ])

    @app.callback(
        Output('prod_h2', 'value'),
        Output('prod_o2', 'value'),
        Output('n2_hb', 'value'),
        Output('prod_nh3', 'value'),
        Output('tail_nh3', 'value'),
        Output('water_h2', 'value'),
        Output('cooling_h2', 'value'),
        Input('mw_elect', 'value')
    )
    def update_outputs(mw):
        if mw is None: mw = 0
        return (
            round((592000 / 2997) * mw, 1),
            round((295504 / 2997) * mw, 1),
            round((201406 / 2997) * mw, 1),
            round((291.7 / 2997) * mw, 1),
            round((4252 / 2997) * mw, 1),
            round((530 / 2997) * mw, 1),
            round((41316 / 2997) * mw, 1)
        )

    return app


# Hook to initialize the Dash app when the blueprint is registered
@nh3balance_bp.record_once
def on_load(state):
    server = state.app
    create_dash_app(server)
