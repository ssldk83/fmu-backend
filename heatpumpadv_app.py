from flask import Blueprint, request, jsonify
import os, uuid

heatpumpadv_bp = Blueprint('heatpumpadv', __name__)

@heatpumpadv_bp.route('/parametric-cop', methods=['GET'])
def parametric_cop():
    try:
        from tespy.networks import Network
        from tespy.components import (
            Condenser, CycleCloser, SimpleHeatExchanger, Pump,
            Sink, Source, Valve, Drum, HeatExchanger, Compressor,
            Splitter, Merge
        )
        from tespy.connections import Connection
        from tespy.tools.characteristics import CharLine
        from tespy.tools.characteristics import load_default_char as ldc
        from CoolProp.CoolProp import PropsSI as PSI

        # Create network
        working_fluid = "NH3"
        nw = Network(T_unit="C", p_unit="bar", h_unit="kJ / kg", m_unit="kg / s")

        # ---- Initial Subsystem ----
        c_in = Source("refrigerant in")
        cons_closer = CycleCloser("consumer cycle closer")
        va = Sink("valve")
        cd = Condenser("condenser")
        rp = Pump("recirculation pump")
        cons = SimpleHeatExchanger("consumer")

        c0 = Connection(c_in, "out1", cd, "in1", label="0")
        c1 = Connection(cd, "out1", va, "in1", label="1")
        c20 = Connection(cons_closer, "out1", rp, "in1", label="20")
        c21 = Connection(rp, "out1", cd, "in2", label="21")
        c22 = Connection(cd, "out2", cons, "in1", label="22")
        c23 = Connection(cons, "out1", cons_closer, "in1", label="23")

        nw.add_conns(c0, c1, c20, c21, c22, c23)

        cd.set_attr(pr1=0.99, pr2=0.99)
        rp.set_attr(eta_s=0.75)
        cons.set_attr(pr=0.99)

        p_cond = PSI("P", "Q", 1, "T", 273.15 + 95, working_fluid) / 1e5
        c0.set_attr(T=170, p=p_cond, fluid={working_fluid: 1})
        c20.set_attr(T=60, p=2, fluid={"water": 1})
        c22.set_attr(T=90)
        cons.set_attr(Q=-230e3)

        nw.solve("design")

        # ---- Add Remaining Components ----
        amb_in = Source("source ambient")
        amb_out = Sink("sink ambient")
        va = Valve("valve")
        dr = Drum("drum")
        ev = HeatExchanger("evaporator")
        su = HeatExchanger("superheater")
        cp1 = Sink("compressor 1")

        nw.del_conns(c1)

        c1 = Connection(cd, "out1", va, "in1", label="1")
        c2 = Connection(va, "out1", dr, "in1", label="2")
        c3 = Connection(dr, "out1", ev, "in2", label="3")
        c4 = Connection(ev, "out2", dr, "in2", label="4")
        c5 = Connection(dr, "out2", su, "in2", label="5")
        c6 = Connection(su, "out2", cp1, "in1", label="6")

        c17 = Connection(amb_in, "out1", su, "in1", label="17")
        c18 = Connection(su, "out1", ev, "in1", label="18")
        c19 = Connection(ev, "out1", amb_out, "in1", label="19")

        nw.add_conns(c1, c2, c3, c4, c5, c6, c17, c18, c19)

        ev.set_attr(pr1=0.99)
        su.set_attr(pr1=0.99, pr2=0.99)
        c4.set_attr(x=0.9, T=5)

        h_sat = PSI("H", "Q", 1, "T", 273.15 + 15, working_fluid) / 1e3
        c6.set_attr(h=h_sat)
        c17.set_attr(T=15, fluid={"water": 1})
        c19.set_attr(T=9, p=1.013)
        nw.solve("design")

        # ---- Final Stage ----
        cp1 = Compressor("compressor 1")
        cp2 = Compressor("compressor 2")
        ic = HeatExchanger("intermittent cooling")
        hsp = Pump("heat source pump")
        sp = Splitter("splitter")
        me = Merge("merge")
        cv = Valve("control valve")
        hs = Source("ambient intake")
        cc = CycleCloser("heat pump cycle closer")

        nw.del_conns(c0, c6, c17)

        c6 = Connection(su, "out2", cp1, "in1", label="6")
        c7 = Connection(cp1, "out1", ic, "in1", label="7")
        c8 = Connection(ic, "out1", cp2, "in1", label="8")
        c9 = Connection(cp2, "out1", cc, "in1", label="9")
        c0 = Connection(cc, "out1", cd, "in1", label="0")
        c11 = Connection(hs, "out1", hsp, "in1", label="11")
        c12 = Connection(hsp, "out1", sp, "in1", label="12")
        c13 = Connection(sp, "out1", ic, "in2", label="13")
        c14 = Connection(ic, "out2", me, "in1", label="14")
        c15 = Connection(sp, "out2", cv, "in1", label="15")
        c16 = Connection(cv, "out1", me, "in2", label="16")
        c17 = Connection(me, "out1", su, "in1", label="17")

        nw.add_conns(c6, c7, c8, c9, c0, c11, c12, c13, c14, c15, c16, c17)

        pr = (c1.p.val / c5.p.val) ** 0.5
        cp1.set_attr(pr=pr)
        ic.set_attr(pr1=0.99, pr2=0.98)
        hsp.set_attr(eta_s=0.75)
        c0.set_attr(p=p_cond, fluid={working_fluid: 1})
        c6.set_attr(h=c5.h.val + 10)
        c8.set_attr(h=c5.h.val + 10)
        c7.set_attr(h=c5.h.val * 1.2)
        c9.set_attr(h=c5.h.val * 1.2)
        c11.set_attr(p=1.013, T=15, fluid={"water": 1})
        c14.set_attr(T=30)

        nw.solve("design")

        # ---- Prepare for offdesign ----
        cp1.set_attr(design=["eta_s"], offdesign=["eta_s_char"])
        cp2.set_attr(design=["eta_s"], offdesign=["eta_s_char"])
        rp.set_attr(design=["eta_s"], offdesign=["eta_s_char"])
        hsp.set_attr(design=["eta_s"], offdesign=["eta_s_char"])
        cons.set_attr(design=["pr"], offdesign=["zeta"])
        cd.set_attr(design=["pr2", "ttd_u"], offdesign=["zeta2", "kA_char"])
        kA_char1 = ldc("heat exchanger", "kA_char1", "DEFAULT", CharLine)
        kA_char2 = ldc("heat exchanger", "kA_char2", "EVAPORATING FLUID", CharLine)
        ev.set_attr(design=["pr1", "ttd_l"], offdesign=["zeta1", "kA_char"],
                    kA_char1=kA_char1, kA_char2=kA_char2)
        su.set_attr(design=["pr1", "pr2", "ttd_u"], offdesign=["zeta1", "zeta2", "kA_char"])
        ic.set_attr(design=["pr1", "pr2"], offdesign=["zeta1", "zeta2", "kA_char"])
        c14.set_attr(design=["T"])

        # ---- Isolated temp file ----
        design_file = f"/tmp/design_{uuid.uuid4().hex}.json"
        nw.save(design_file)
        nw.solve("offdesign", design_path=design_file)

        # ---- Results ----
        q_out = cons.Q.val
        w_in = cp1.P.val + cp2.P.val + rp.P.val + hsp.P.val
        cop = abs(q_out) / w_in if w_in != 0 else None

        # Clean up temp file
        os.remove(design_file)

        return jsonify({
            "status": "success",
            "COP": round(cop, 3),
            "Q_output_kW": round(q_out / 1e3, 2),
            "Power_input_kW": round(w_in / 1e3, 2),
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})
