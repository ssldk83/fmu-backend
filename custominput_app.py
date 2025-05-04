from flask import Blueprint, jsonify, request
import shutil
import traceback
from uuid import uuid4
from fmpy import read_model_description, extract
from fmpy.fmi2 import FMU2Slave

custominput_bp = Blueprint('custominput', __name__)

# Store all sessions here: { session_id: simulation_state }
sessions = {}

@custominput_bp.route('/start-simulation', methods=['POST'])
def start_simulation():
    try:
        # Create unique session ID
        session_id = str(uuid4())

        # Load the FMU from disk (must be pre-uploaded alongside this script)
        fmu_filename = 'PumpWithPIDControl.fmu'
        print(f"[INFO] Starting simulation for session {session_id} using FMU: {fmu_filename}")

        model_description = read_model_description(fmu_filename)
        vrs = {var.name: var.valueReference for var in model_description.modelVariables}

        unzipdir = extract(fmu_filename)
        vr_input = vrs.get('flowSetpoint')
        vr_actual_flow = vrs.get('actualFlow')
        vr_power_consumption = vrs.get('powerConsumption')

        if vr_input is None or vr_actual_flow is None or vr_power_consumption is None:
            raise Exception("Could not find required variables ('flowSetpoint', 'actualFlow', or 'powerConsumption') in the FMU.")

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
            'step_size': 1.e-1,  # 0.1 seconds
            'stop_time': 31536000,  # 1 year in seconds
            'threshold': 200.0,  # Optional: you can remove this if not needed
            'unzipdir': unzipdir,
            'vr_input': vr_input,
            'vr_actual_flow': vr_actual_flow,
            'vr_power_consumption': vr_power_consumption,
            'done': False
        }

        return jsonify({'message': 'Simulation started successfully!', 'session_id': session_id})

    except Exception as e:
        print(f"[ERROR] Error in /start-simulation: {e}")
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
        cleanup_session(session_id)
        return jsonify({'done': True})

    fmu = sim['fmu']
    time = sim['time']
    step_size = sim['step_size']
    stop_time = sim['stop_time']
    threshold = sim['threshold']
    vr_input = sim['vr_input']
    vr_actual_flow = sim['vr_actual_flow']
    vr_power_consumption = sim['vr_power_consumption']

    try:
        # Set input and perform a simulation step
        fmu.setReal([vr_input], [input_value])
        fmu.doStep(currentCommunicationPoint=time, communicationStepSize=step_size)
        time += step_size
        sim['time'] = time

        # Read output
        actual_flow, power_consumption = fmu.getReal([vr_actual_flow, vr_power_consumption])

        # Check if simulation is done
        if time >= stop_time or actual_flow > threshold:
            sim['done'] = True
            cleanup_session(session_id)

        return jsonify({
            'time': time,
            'flowSetpoint': input_value,
            'actualFlow': actual_flow,
            'powerConsumption': power_consumption,
            'done': sim['done']
        })

    except Exception as e:
        print(f"[ERROR] Error in /step-simulation for session {session_id}: {e}")
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
        print(f"[INFO] Cleaning up session {session_id}")
        try:
            sim['fmu'].terminate()
            sim['fmu'].freeInstance()
        except Exception as e:
            print(f"[WARNING] Error cleaning up FMU for session {session_id}: {e}")
        if sim['unzipdir']:
            shutil.rmtree(sim['unzipdir'], ignore_errors=True)
