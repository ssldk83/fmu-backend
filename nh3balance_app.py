# nh3balance_app.py

from flask import Blueprint, request, jsonify

nh3balance_bp = Blueprint('nh3balance', __name__, url_prefix='/nh3balance')

@nh3balance_bp.route('/calculate', methods=['POST'])
def calculate_nh3balance():
    try:
        data = request.get_json()
        mw = data.get('mw_elect', 0)

        # Validate input
        try:
            mw = float(mw)
        except (TypeError, ValueError):
            return jsonify({'error': 'Invalid input: mw_elect must be a number.'}), 400

        results = {
            'prod_h2': round((592000 / 2997) * mw, 1),
            'prod_o2': round((295504 / 2997) * mw, 1),
            'n2_hb': round((201406 / 2997) * mw, 1),
            'prod_nh3': round((291.7 / 2997) * mw, 1),
            'tail_nh3': round((4252 / 2997) * mw, 1),
            'water_h2': round((530 / 2997) * mw, 1),
            'cooling_h2': round((41316 / 2997) * mw, 1)
        }

        return jsonify(results)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@nh3balance_bp.route('/', methods=['GET'])
def home():
    return jsonify({'message': 'NH3 balance API ready. POST to /calculate with {"mw_elect": <value>}'})
