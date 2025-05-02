# custominput_app.py

from flask import Blueprint, jsonify, request
from flask_cors import CORS
import shutil
import traceback
from uuid import uuid4
from fmpy import read_model_description, extract
from fmpy.fmi2 import FMU2Slave
from fmpy.util import download_test_file

custominput_bp = Blueprint('custominput', __name__)
CORS(custominput_bp)

# Store all sessions here: { session_id: simulation_state }
sessions = {}


@custominput_bp.route('/start-simulation', methods=['POST'])
def start_simulation():
    try:
        # Create unique session ID
        session_id = str(uuid4())

        # Download and prepare the FMU
        fmu_filename = 'CoupledClutches.fmu'
        download_test_file('2.0', 'CoSimulation', 'MapleSim', '2016.2', 'CoupledClutches', fmu_filename)
        model_description = read_model_description(fmu_filename)
        vrs = {var.name: var.valueReference for var in model_description.modelVariables}

        unzipdir = extract(fmu_filename)
        vr_inputs = vrs['inputs']
        vr_outputs4 = vrs['outputs[4]']

        # Initialize the FMU
        fmu = FMU2Slave(
            guid=model_description.guid,
            unzipDirectory=unzipdir,
            modelIdentifier=model_description.coSimulation.modelIdentifier,
            instanceName=session_id
        )
        fmu.instantiate()
        fmu.setupExperiment(startTime=0.0)
        fmu.enterInitializationMode()
        fmu.exitInitializationMode()

        # Save the simulation state for this session
        sessions[session_id] = {
            'fmu': fmu,
            'time': 0.0,
            'step_size': 1e-3,
            'stop_time': 2.0,
            'threshold': 2.0,
            'unzipdir': unzipdir,
            'vr_inputs': vr_inputs,
            'vr_outputs4': vr_outputs4,
            'done': False
        }

        return jsonify({'message': 'Simulation started successfully!', 'session_id': session_id})

    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@custominput_bp.route('/step-simulation', methods=['POST'])
def step_simulation():
    data = request.get_json()
    session_id = data.get('session_id')
    input_value = data.get('input_value', 0.0)

    if not session_id or session_id not in sessions:
        return jsonify({'error': 'Invalid or missing session_id.'}), 400

    sim = sessions[session_id]

    if sim['done']:
        # Clean up session after it's done
        cleanup_session(session_id)
        return jsonify({'done': True})

    fmu = sim['fmu']
    time = sim['time']
    step_size = sim['step_size']
    stop_time = sim['stop_time']
    threshold = sim['threshold']
    vr_inputs = sim['vr_inputs']
    vr_outputs4 = sim['vr_outputs4']

    try:
        # Set input and perform a simulation step
        fmu.setReal([vr_inputs], [input_value])
        fmu.doStep(currentCommunicationPoint=time, communicationStepSize=step_size)
        time += step_size
        sim['time'] = time

        # Read output
        inputs, outputs4 = fmu.getReal([vr_inputs, vr_outputs4])

        # Check if simulation is done
        if time >= stop_time or outputs4 > threshold:
            sim['done'] = True
            cleanup_session(session_id)

        return jsonify({
            'time': time,
            'inputs': inputs,
            'outputs4': outputs4,
            'done': sim['done']
        })

    except Exception as e:
        traceback.print_exc()
        cleanup_session(session_id)
        return jsonify({'error': str(e)}), 500


@custominput_bp.route('/')
def home():
    return 'Real-Time FMU Simulation API (multi-user ready)'


def cleanup_session(session_id):
    """Free resources and remove the session."""
    sim = sessions.pop(session_id, None)
    if sim:
        try:
            sim['fmu'].terminate()
            sim['fmu'].freeInstance()
        except Exception:
            pass
        if sim['unzipdir']:
            shutil.rmtree(sim['unzipdir'], ignore_errors=True)
