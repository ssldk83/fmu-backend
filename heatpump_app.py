from flask import Blueprint, request, jsonify
from tespy.networks import Network
from tespy.components import CycleCloser, Compressor, Valve, SimpleHeatExchanger
from tespy.connections import Connection

heatpump_bp = Blueprint('heatpump', __name__)

@heatpump_bp.route('/simulate', methods=['GET'])
def simulate_heatpump():
    try:
        # Get inputs from query parameters
        evap_T = float(request.args.get('evap_T', 20))     # °C
        cond_T = float(request.args.get('cond_T', 80))     # °C
        fluid = request.args.get('fluid', 'R134a')         # default fluid

        # Create network
        my_plant = Network(fluids=[fluid])
        my_plant.set_attr(T_unit='C', p_unit='bar', h_unit='kJ / kg')

        # Components
        cc = CycleCloser('cycle closer')
        co = SimpleHeatExchanger('condenser')
        ev = SimpleHeatExchanger('evaporator')
        va = Valve('expansion valve')
        cp = Compressor('compressor')

        # Connections
        c1 = Connection(cc, 'out1', ev, 'in1', label='1')
        c2 = Connection(ev, 'out1', cp, 'in1', label='2')
        c3 = Connection(cp, 'out1', co, 'in1', label='3')
        c4 = Connection(co, 'out1', va, 'in1', label='4')
        c0 = Connection(va, 'out1', cc, 'in1', label='0')
        my_plant.add_conns(c1, c2, c3, c4, c0)

        # Set attributes
        co.set_attr(pr=0.98, Q=-1e6)
        ev.set_attr(pr=0.98)
        cp.set_attr(eta_s=0.85)

        c2.set_attr(T=evap_T, x=1, fluid={fluid: 1})
        c4.set_attr(T=cond_T, x=0)

        # Solve
        my_plant.solve(mode='design')
        cop = abs(co.Q.val) / cp.P.val

        return jsonify({
            'status': 'success',
            'COP': round(cop, 3),
            'cp_power_kW': round(cp.P.val / 1e3, 2),
            'condenser_Q_kW': round(abs(co.Q.val) / 1e3, 2),
            'inputs': {
                'evaporator_T_C': evap_T,
                'condenser_T_C': cond_T,
                'fluid': fluid
            }
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})
