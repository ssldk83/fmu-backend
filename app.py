from flask import Flask, request, jsonify
from flask_cors import CORS
import fmpy

app = Flask(__name__)
CORS(app)

FMU_FILENAME = 'SecondOrderSystem.fmu'  # Change this if your FMU filename is different

@app.route('/')
def home():
    return "FMU Backend is up and running!"

@app.route('/simulate_get', methods=['GET'])
def simulate_get():
    return "Use POST method on /simulate to run the FMU simulation."

@app.route('/simulate', methods=['POST'])
def simulate():
    try:
        result = fmpy.simulate_fmu(FMU_FILENAME, stop_time=10)

        # Convert numpy structured array to JSON-serializable dict
        output = {key: result[key].tolist() for key in result.dtype.names}
        return jsonify(output)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
