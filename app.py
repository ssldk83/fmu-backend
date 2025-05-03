from flask import Flask
from custominput_app import custominput_bp
from nh3balance_app import nh3balance_bp
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Add this to enable CORS globally

app.register_blueprint(custominput_bp, url_prefix='/custominput')
app.register_blueprint(nh3balance_bp, url_prefix='/nh3balance')

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
