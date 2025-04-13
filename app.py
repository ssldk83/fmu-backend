from flask import Flask, request, jsonify
from flask_cors import CORS
import fmpy

app = Flask(__name__)
CORS(app)

@app.route('/simulate', methods=['POST'])
def simulate():
    data = request.json
    stop_time = data.get('stop_time', 10)
    parameters = data.get('parameters', {})  # Accepts dynamic parameters

    result = fmpy.simulate_fmu(
        'SecondOrderSystem.fmu',
        stop_time=stop_time,
        start_values=parameters
    )

    return jsonify({k: result[k].tolist() for k in result.dtype.names})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
