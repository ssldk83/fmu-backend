from flask import Flask
from flask_cors import CORS

################################### run flas app
app = Flask(__name__)
CORS(app)

################################### import apps
from custominput_app import custominput_bp
from nh3balance_app import nh3balance_bp
from heatpump_app import heatpump_bp
from heatpumpadv_app import heatpumpadv_bp
from pysam_lcoh_app import pysam_lcoh_bp

################################### rout to the apps
app.register_blueprint(custominput_bp, url_prefix='/custominput')
app.register_blueprint(nh3balance_bp, url_prefix='/nh3balance')
app.register_blueprint(heatpump_bp, url_prefix='/heatpump')
app.register_blueprint(heatpumpadv_bp, url_prefix='/heatpumpadv')
app.register_blueprint(pysam_lcoh_bp, url_prefix='/pysam')

#################################### Port
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
