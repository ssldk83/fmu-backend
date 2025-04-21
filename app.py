# app.py
from flask import Flask
from dash import Dash, html
from firstorder_app import init_firstorder
from nh3balance_app import init_nh3balance
from cv_app import init_cv
#from realtimeoscillator_app import init_realtimeoscillator

server = Flask(__name__)  # ✅ Create the Flask app
app = Dash(__name__, server=server, suppress_callback_exceptions=True)  # Main Dash app for Render

# Optional main layout placeholder

app.layout = html.Div([
    html.H1("FMU Dashboard Hub"),
    html.P("Visit /firstorder/ or /nh3balance/")
], className="dash-container")

# Attach subapps to the same server
init_firstorder(server)
init_nh3balance(server)
#init_realtimeoscillator(server)
init_cv(server)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
