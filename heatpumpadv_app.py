from flask import Blueprint, request, jsonify
from tespy.networks import Network
from tespy.components import (
    Condenser, CycleCloser, SimpleHeatExchanger, Pump, Sink, Source, Valve,
    Drum, HeatExchanger, Compressor, Splitter, Merge
)
from tespy.connections import Connection
from tespy.tools.characteristics import CharLine
from tespy.tools.characteristics import load_default_char as ldc
from CoolProp.CoolProp import PropsSI as PSI
import numpy as np

heatpumpadv_bp = Blueprint('heatpumpadv', __name__)

@heatpumpadv_bp.route('/parametric-cop', methods=['GET'])
def parametric_cop():
    try:
        working_fluid = request.args.get("fluid", "R717")
        evap_T = float(request.args.get("evap_T", 5))
        cond_T = float(request.args.get("cond_T", 60))

        nw = Network(T_unit="C", p_unit="bar", h_unit="kJ / kg", m_unit="kg / s")
        nw.set_attr(iterinfo=False)

        # Minimal system for parametric simulation
        cons_closer = CycleCloser("consumer cycle closer")
        rp = Pump("recirculation pump")
        cons = SimpleHeatExchanger("consumer")
        cd = Condenser("condenser")
        c0 = Source("refrigerant in")
        c1 = Sink("valve")

        # Connections
        con0 = Connection(c0, "out1", cd, "in1")
        con1 = Connection(cd, "out1", c1, "in1")
        con20 = Connection(cons_closer, "out1", rp, "in1")
        con21 = Connection(rp, "out1", cd, "in2")
        con22 = Connection(cd, "out2", cons, "in1")
        con23 = Connection(cons, "out1", cons_closer, "in1")
        nw.add_conns(con0, con1, con20, con21, con22, con23)

        # Attributes
        p_cond = PSI("P", "Q", 1, "T", 273.15 + cond_T, working_fluid) / 1e5
        con0.set_attr(T=170, p=p_cond, fluid={working_fluid: 1})
        con20.set_attr(T=60, p=2, fluid={"water": 1})
        con22.set_attr(T=90)

        cd.set_attr(pr1=0.99, pr2=0.99)
        rp.set_attr(eta_s=0.75)
        cons.set_attr(pr=0.99)
        cons.set_attr(Q=-230e3)

        nw.solve("design")
        cd.set_attr(ttd_u=5)
        cons.set_attr(design=["pr"], offdesign=["zeta"])
        rp.set_attr(design=["eta_s"], offdesign=["eta_s_char"])

        kA_char1 = ldc("heat exchanger", "kA_char1", "DEFAULT", CharLine)
        kA_char2 = ldc("heat exchanger", "kA_char2", "EVAPORATING FLUID", CharLine)
        cons.set_attr(kA_char1=kA_char1, kA_char2=kA_char2, offdesign=["zeta", "kA_char"])

        nw.save("system_design.json")

        # Parametric analysis over heat load
        cop_results = []
        for Q in np.linspace(1, 0.6, 5) * cons.Q.val:
            cons.set_attr(Q=Q)
            nw.solve("offdesign", design_path="system_design.json")
            total_power = rp.P.val
            cop = abs(cons.Q.val) / total_power if total_power > 0 else None
            cop_results.append({
                "Q_kW": round(abs(cons.Q.val) / 1e3, 2),
                "COP": round(cop, 2) if cop else None
            })

        return jsonify({
            "status": "success",
            "fluid": fluid,
            "evap_T_C": evap_T,
            "cond_T_C": cond_T,
            "results": cop_results
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})
