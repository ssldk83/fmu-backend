from flask import Flask, request, jsonify
from flask_cors import CORS
import fmpy

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "FMU Backend is up and running!"

@app.route('/simulate_get', methods=['GET'])
def simulate_get():
    return "Use POST method with JSON data to simulate the FMU."

from flask import Flask, jsonify
from flask_cors import CORS
import fmpy

app = Flask(__name__)
CORS(app)

@app.route('/simulate', methods=['POST'])
def simulate():
    try:
        result = fmpy.simulate_fmu('SecondOrderSystem.fmu', stop_time=10)

        # Return all outputs including time
        return jsonify({k: result[k].tolist() for k in result.dtype.names})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
