from flask import Flask
from flask_cors import CORS

################################### run flas app
app = Flask(__name__)
CORS(app)

################################### import apps
from custominput_app import custominput_bp
from nh3balance_app import nh3balance_bp
from heatpump_app import heatpump_bp
from heatpumpadv_app import heatpumpadv_bp

################################### rout to the apps
app.register_blueprint(custominput_bp, url_prefix='/custominput')
app.register_blueprint(nh3balance_bp, url_prefix='/nh3balance')
app.register_blueprint(heatpump_bp, url_prefix='/heatpump')
app.register_blueprint(heatpumpadv_bp, url_prefix='/heatpumpadv')

#################################### Port
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
# app.py (add or replace with this minimal shape)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="G4iE Energy API", version="v1")

ALLOWED_ORIGINS = [
    "https://<your-project>.vercel.app",
    "https://app.g4ie.dk",  # if you attach the domain
    "https://<your-framer-site>.framer.website"  # if you embed from Framer
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class HPSimple(BaseModel):
    heat_duty_mw: float
    cop: float
    power_price_eur_per_mwh: float
    capex_eur: float
    om_frac: float = 0.03
    util_pct: float = 85
    lifetime_years: int = 10
    wacc_pct: float = 8

@app.get("/api/v1/healthz")
def healthz():
    return {"ok": True}

@app.post("/api/v1/run/hp")
def run_hp(m: HPSimple):
    elec_mw = m.heat_duty_mw / m.cop
    heat_mwh_year = m.heat_duty_mw * 8760 * (m.util_pct/100)
    elec_mwh_year = elec_mw * 8760 * (m.util_pct/100)
    crf = (m.wacc_pct/100) / (1 - (1 + m.wacc_pct/100)**(-m.lifetime_years))
    annualized_capex = m.capex_eur * crf
    opex_eur = elec_mwh_year * m.power_price_eur_per_mwh + m.capex_eur*m.om_frac
    lcoa = (annualized_capex + opex_eur) / heat_mwh_year
    return {
        "results": {
            "elec_mw": elec_mw,
            "heat_mwh_year": heat_mwh_year,
            "lcoa_eur_per_mwh": round(lcoa, 2),
            "capex_annualized_eur": round(annualized_capex, 2),
            "opex_eur": round(opex_eur, 2),
        }
    }
