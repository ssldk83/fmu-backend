from flask import Blueprint, request, jsonify
from flask_cors import CORS
import PySAM.Electrolysis as Electrolysis

pysam_lcoh_bp = Blueprint('pysam_lcoh_bp', __name__)
CORS(pysam_lcoh_bp)

@pysam_lcoh_bp.route('/pysam-lcoh', methods=['GET'])
def calculate_lcoh():
    try:
        # User inputs
        elec_price = float(request.args.get('elec_price', 40))  # $/MWh
        capex = float(request.args.get('capex', 1000))          # $/kW
        electrolyzer_capacity = float(request.args.get('capacity', 10000))  # kW
        annual_h2_production_kg = float(request.args.get('h2prod', 450000))  # kg/year
        lifetime = int(request.args.get('lifetime', 20))
        discount = float(request.args.get('discount', 0.08))

        # Create model
        model = Electrolysis.default("ElectrolyzerStandalone")
        model.SystemDesign.electrolyzer_system_capacity_kw = electrolyzer_capacity
        model.SystemDesign.electrolyzer_system_cost_kw = capex
        model.Electrolyzer.elec_cost_per_kwh = elec_price / 1000  # Convert to $/kWh

        # Financial parameters (simplified)
        capex_total = capex * electrolyzer_capacity
        opex = 0.03 * capex_total
        annuity = (capex_total * discount) / (1 - (1 + discount)**(-lifetime))
        annual_cost = annuity + opex + (elec_price / 1000) * model.SystemDesign.electrolyzer_system_capacity_kw * 8760 * 0.5  # assume 50% CF
        lcoh = annual_cost / annual_h2_production_kg

        return jsonify({
            "status": "success",
            "inputs": {
                "CAPEX ($/kW)": capex,
                "Electricity Price ($/MWh)": elec_price,
                "Capacity (kW)": electrolyzer_capacity,
                "Annual H2 production (kg)": annual_h2_production_kg
            },
            "lcoh": round(lcoh, 2)
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})
