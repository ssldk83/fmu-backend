from flask import Flask
from flask_cors import CORS

################################### run flas app
app = Flask(__name__)
CORS(app)

################################### import apps
from custominput_app import custominput_bp
from nh3balance_app import nh3balance_bp
from oandm_app import oandm_bp

################################### rout to the apps
app.register_blueprint(custominput_bp, url_prefix='/custominput')
app.register_blueprint(nh3balance_bp, url_prefix='/nh3balance')
app.register_blueprint(oandm_bp, url_prefix='/oandm')

#################################### Port
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
