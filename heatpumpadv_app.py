from flask import Blueprint, request, jsonify
heatpumpadv_bp = Blueprint('heatpumpadv', __name__)
@heatpumpadv_bp.route('/parametric-cop', methods=['GET'])
def parametric_cop():
    try:
        from tespy.networks import Network
        from tespy.components import (
            Condenser, CycleCloser, SimpleHeatExchanger, Pump, Sink, Source, Valve,
            Drum, HeatExchanger, Compressor, Splitter, Merge
        )
        from tespy.connections import Connection
        from CoolProp.CoolProp import PropsSI as PSI

        working_fluid = "NH3"
        nw = Network(T_unit="C", p_unit="bar", h_unit="kJ / kg", m_unit="kg / s")
        
        # Components
        cd = Condenser("condenser")
        rp = Pump("recirculation pump")
        cons = SimpleHeatExchanger("consumer")
        va = Valve("valve")
        dr = Drum("drum")
        ev = HeatExchanger("evaporator")
        su = HeatExchanger("superheater")
        cp1 = Compressor("compressor 1")
        cp2 = Compressor("compressor 2")
        ic = HeatExchanger("intermittent cooling")
        hsp = Pump("heat source pump")
        sp = Splitter("splitter")
        me = Merge("merge")
        cv = Valve("control valve")
        hs = Source("ambient intake")
        cc = CycleCloser("heat pump cycle closer")
        amb_out = Sink("sink ambient")
        cons_closer = CycleCloser("consumer cycle closer")
        
        # Connections
        c0 = Connection(cc, "out1", cd, "in1", label="0")
        c1 = Connection(cd, "out1", va, "in1", label="1")
        c2 = Connection(va, "out1", dr, "in1", label="2")
        c3 = Connection(dr, "out1", ev, "in2", label="3")
        c4 = Connection(ev, "out2", dr, "in2", label="4")
        c5 = Connection(dr, "out2", su, "in2", label="5")
        c6 = Connection(su, "out2", cp1, "in1", label="6")
        c7 = Connection(cp1, "out1", ic, "in1", label="7")
        c8 = Connection(ic, "out1", cp2, "in1", label="8")
        c9 = Connection(cp2, "out1", cc, "in1", label="9")
        c11 = Connection(hs, "out1", hsp, "in1", label="11")
        c12 = Connection(hsp, "out1", sp, "in1", label="12")
        c13 = Connection(sp, "out1", ic, "in2", label="13")
        c14 = Connection(ic, "out2", me, "in1", label="14")
        c15 = Connection(sp, "out2", cv, "in1", label="15")
        c16 = Connection(cv, "out1", me, "in2", label="16")
        c17 = Connection(me, "out1", su, "in1", label="17")
        c18 = Connection(su, "out1", ev, "in1", label="18")
        c19 = Connection(ev, "out1", amb_out, "in1", label="19")
        c20 = Connection(cons_closer, "out1", rp, "in1", label="20")
        c21 = Connection(rp, "out1", cd, "in2", label="21")
        c22 = Connection(cd, "out2", cons, "in1", label="22")
        c23 = Connection(cons, "out1", cons_closer, "in1", label="23")

        nw.add_conns(c0, c1, c2, c3, c4, c5, c6, c7, c8, c9, c11, c12, c13, c14, c15, c16, c17, c18, c19, c20, c21, c22, c23)

        # Parametrization
        cd.set_attr(pr1=0.99, pr2=0.99)
        rp.set_attr(eta_s=0.75)
        ev.set_attr(pr1=0.99)
        su.set_attr(pr1=0.99, pr2=0.99)
        cons.set_attr(pr=0.99, Q=-230e3)
        cp1.set_attr(pr=3.0)
        ic.set_attr(pr1=0.99, pr2=0.98)
        hsp.set_attr(eta_s=0.75)
        
        p_cond = PSI("P", "Q", 1, "T", 273.15 + 95, working_fluid) / 1e5 # bar
        c0.set_attr(T=170, p=p_cond, fluid={working_fluid: 1})        
        c4.set_attr(x=0.9, T=5)
        c6.set_attr(h=c5.h.val + 10)
        c11.set_attr(p=1.013, T=15, fluid={"water": 1})
        c14.set_attr(T=30)
        c17.set_attr(T=15, fluid={"water": 1})
        c19.set_attr(T=9, p=1.013)
        c20.set_attr(T=60, p=2, fluid={"water": 1})
        c22.set_attr(T=90)

        #*********************** Solve
        print("DoF before solve:", nw.lin_dep)  # Shows how many degrees of freedom are missing
        nw.solve("design")

        #*********************** Set Final System Parameters
        c0.set_attr(p=None)
        cd.set_attr(ttd_u=5)
        c4.set_attr(T=None)
        ev.set_attr(ttd_l=5)
        c6.set_attr(h=None)
        su.set_attr(ttd_u=5)
        c7.set_attr(h=None)
        cp1.set_attr(eta_s=0.8)
        c9.set_attr(h=None)
        cp2.set_attr(eta_s=0.8)
        c8.set_attr(h=None, Td_bp=4)
        nw.solve("design")

        # Extract results (e.g., COP)
        q_out = cons.Q.val  # Heat delivered to consumer [W]
        w_in = cp1.P.val + cp2.P.val + rp.P.val + hsp.P.val  # Total work input [W]
        cop = abs(q_out) / w_in if w_in != 0 else None
        
        return jsonify({
            "status": "success",
            "COP": round(cop, 3),
            "Q_output_kW": round(q_out / 1e3, 2),
            "Power_input_kW": round(w_in / 1e3, 2)
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})
