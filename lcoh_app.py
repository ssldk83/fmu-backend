from flask import Blueprint, request, jsonify
from flask_cors import CORS
import numpy as np
from pyH2A.Project import Project

lcoh_bp = Blueprint('lcoh_bp', __name__)
CORS(lcoh_bp)

@lcoh_bp.route('/lcoh', methods=['GET'])
def calculate_lcoh():
    try:
        # Get input parameters from query string
        capex = float(request.args.get('capex', 1000))  # $/kW
        opex = float(request.args.get('opex', 3))       # % of capex
        elec_price = float(request.args.get('elec_price', 50))  # $/MWh
        elec_consumption = float(request.args.get('elec_consumption', 50))  # kWh/kg H2
        efficiency = float(request.args.get('efficiency', 70))  # %
        
        # Create Project with custom assumptions
        overrides = {
            'Installed Capacity [MW]': 10,
            'Electrolyzer CAPEX [$/kW]': capex,
            'Fixed OPEX [% of CAPEX]': opex,
            'Electricity Price [$/MWh]': elec_price,
            'Electricity Consumption [kWh/kg]': elec_consumption,
            'Efficiency [%]': efficiency
        }

        p = Project('PEM Electrolysis', override_parameters=overrides)
        lcoh = p.get_LCOH()

        return jsonify({
            'status': 'success',
            'inputs': overrides,
            'lcoh': round(lcoh, 2)
        })

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})
