from flask import Flask, render_template
from flask_cors import CORS

################################### run flas app
app = Flask(__name__)
CORS(app)

################################### import apps
from custominput_app import custominput_bp
from nh3balance_app import nh3balance_bp

################################### rout to the apps
app.register_blueprint(custominput_bp, url_prefix='/custominput')
app.register_blueprint(nh3balance_bp, url_prefix='/nh3balance')

#################################### Port
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
