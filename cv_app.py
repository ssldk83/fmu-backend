# cv_generator_app.py (modular Dash app for Flask server, PDF output, editable text in code)
import dash
from dash import html, dcc, Input, Output, State
import base64
from io import BytesIO
from weasyprint import HTML

# Static CV text (edit this directly to update your CV)
cv_text = """
Saeed S. Lafmejani
Process / Project Engineer
Address: 9260 Gistrup, Denmark
Passport: Danish
Phone: +45-2678-2233
Email: ssl@G4iE.dk
CVR: 45118711

Summary
As a consultant, I specialize in preparing high-quality Process Flow Diagrams (PFDs), P&IDs, and component lists using AutoCAD Plant. I also develop heat and mass balances to support the design of PtX, CCUS, Biogas, and Power Plants.

Professional Experience
Self-Employed – G4iE ApS
- Site inspection of a power-to-ammonia plant in Denmark.
- PFD and P&ID development for biogas plants in Belgium and the UK.
- Design of a MW-scale air-source heat pump plant.
- Innovation within PtX and CCUS.

Senior Specialist – COWI
- Process design for 1GW hydrogen plant (PlugPower).
- PFDs, P&IDs, vent system design for hydrogen and oxygen.
- Feasibility studies and simulations for hydrogen and carbon capture.
- Contributor to Energistyrelsen tech data for CCS.

PtX Senior Process Engineer – Blue Power Partners
- Techno-economic assessment of green ammonia in Morocco and Chile.
- LCoA modeling and CAPEX/OPEX estimates.

Project Engineer – Nature Energy A/S
- Detailed design of biogas plants: PFDs, P&IDs, H&M balances.
- Integration of electrolyzer and bio-trickling filter for methane boosting.
- Equipment sizing, piping design, and risk analysis.

PhD – Aalborg University
- Design and simulation of PEM water electrolysis systems.
- Research presented at international conferences.

Internship – Forschungszentrum Jülich
- Large stack electrolyzer design and efficiency improvement.

Education
PhD in Water Electrolysis, Aalborg University

Languages
English, Danish

Technical Skills
Process Simulation: HYSYS, FLARE, AutoCAD Plant
Safety: PED, ISO 22734, API 520/521
Programming:
- Process Design: PFDs, P&IDs, H&M balances
- Equipment Sizing: Pumps, Compressors, Heat Exchangers
- Safety Analysis: HAZOP, SIL, LOPA
- Software: HYSYS, FLARE, AutoCAD Plant
- Programming: Python, Excel VBA
"""

def init_cv(server):
    app = dash.Dash(
        __name__,
        server=server,
        url_base_pathname='/cv/',
        suppress_callback_exceptions=True
    )

    app.layout = html.Div([
        html.H2("Generate Domain-Specific CV"),

        html.Label("Select Expertise Area:"),
        dcc.Dropdown(
            id="domain-select",
            options=[
                {"label": "Biogas", "value": "biogas"},
                {"label": "Green Hydrogen", "value": "hydrogen"},
                {"label": "Power-to-X", "value": "ptx"},
                {"label": "All Experience", "value": "all"}
            ],
            value="all",
            style={"width": "300px"}
        ),

        html.Button("Generate CV", id="generate-button", n_clicks=0),
        html.Div(id="download-link")
    ], style={"maxWidth": "500px", "margin": "auto", "padding": "2rem"})

    @app.callback(
        Output("download-link", "children"),
        Input("generate-button", "n_clicks"),
        State("domain-select", "value")
    )
    def generate_cv(n_clicks, domain):
        if n_clicks == 0:
            return ""

        keep_phrases = {
            "biogas": ["biogas", "Nature Energy"],
            "hydrogen": ["hydrogen", "electrolysis", "PEM", "HYSYS", "PlugPower"],
            "ptx": ["Power-to-X", "PtX", "green ammonia", "LCoA", "Blue Power"]
        }

        html_lines = []
        for line in cv_text.splitlines():
            if domain == "all" or any(k.lower() in line.lower() for k in keep_phrases[domain]):
                html_lines.append(f"<p>{line}</p>")

        html_content = f"""
        <html><body style='font-family:Arial;padding:20px;'>
        {''.join(html_lines)}
        </body></html>
        """

        output = BytesIO()
        HTML(string=html_content).write_pdf(output)
        encoded_pdf = base64.b64encode(output.getvalue()).decode()

        return html.A("📄 Download CV (PDF)", href=f"data:application/pdf;base64,{encoded_pdf}",
                      download=f"cv_{domain}.pdf", target="_blank")
