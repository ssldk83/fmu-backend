from flask import Flask, render_template

################################### import apps
from custominput_app import custominput_bp
from nh3balance_app import nh3balance_bp
from flask_cors import CORS

################################### run flas app
app = Flask(__name__)
CORS(app)  # Add this to enable CORS globally

################################### rout to the apps
app.register_blueprint(landing_pages_bp, url_prefix=')
app.register_blueprint(custominput_bp, url_prefix='/custominput')
app.register_blueprint(nh3balance_bp, url_prefix='/nh3balance')

#################################### Landing page routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

#################################### Port
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
