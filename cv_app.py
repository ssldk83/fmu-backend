# cv_generator_app.py (modular Dash app for Flask server, full-text PDF CV)
import dash
from dash import html, dcc, Input, Output, State
import base64
from io import BytesIO
from weasyprint import HTML

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

        # Full HTML CV content pasted directly here
        full_html = '''
        <!DOCTYPE html>
        <html>
        <head>
        <meta charset="utf-8">
        <style>
            @page { size: A4; margin: 2cm; }
            body { font-family: 'Segoe UI', sans-serif; font-size: 11pt; color: #222; line-height: 1.5; }
            h1, h2, h3 { color: #004080; margin-top: 1.2em; }
            p, li { margin: 0.3em 0; }
            ul { padding-left: 1.2em; }
            .header { display: flex; justify-content: space-between; border-bottom: 2px solid #888; padding-bottom: 1em; margin-bottom: 2em; }
            .photo { width: 100px; }
            .photo img { width: 100%; border-radius: 8px; }
        </style>
        </head>
        <body>
        <div class="header">
            <div>
                <h1>Saeed S. Lafmejani</h1>
                <p><strong>Process / Project Engineer</strong><br>
                9260 Gistrup, Denmark<br>
                Danish passport<br>
                Email: ssl@G4iE.dk<br>
                Phone: +45-2678-2233<br>
                CVR: 45118711</p>
            </div>
            <div class="photo">
                <img src="image1.jpg" alt="Saeed photo">
            </div>
        </div>

        <h2>Summary</h2>
        <p>Consultant focused on Process Flow Diagrams (PFDs), P&IDs, and process design for PtX, CCUS, Biogas, and Power Plants using AutoCAD Plant and Excel-based tools.</p>

        <h2>Professional Experience</h2>
        <h3>Self-Employed – G4iE ApS</h3>
        <ul>
            <li>Site inspection of a power-to-ammonia plant in Denmark</li>
            <li>PFD & P&ID design for biogas plants in Belgium and UK</li>
            <li>MW-scale air-source heat pump system design</li>
            <li>Innovation in PtX and CCUS technologies</li>
        </ul>
        <h3>Senior Specialist – COWI</h3>
        <ul>
            <li>Process design of 1GW hydrogen plant (PlugPower)</li>
            <li>PFDs, P&IDs, and vent system design for H2/O2</li>
            <li>Feasibility studies and HYSYS simulations</li>
            <li>CCUS technical data support to Danish Energy Agency</li>
        </ul>
        <h3>PtX Senior Engineer – Blue Power Partners</h3>
        <ul>
            <li>Techno-economic assessments of green ammonia projects</li>
            <li>LCoA modeling and CAPEX/OPEX estimation</li>
        </ul>
        <h3>Project Engineer – Nature Energy A/S</h3>
        <ul>
            <li>Design of biogas plants: PFDs, P&IDs, H&M balances</li>
            <li>Electrolyzer and bio-trickling filter integration</li>
            <li>Equipment sizing and safety/risk analysis</li>
        </ul>
        <h3>PhD – Aalborg University</h3>
        <ul>
            <li>Design and simulation of PEM electrolysis systems</li>
            <li>Published and presented in international conferences</li>
        </ul>
        <h3>Internship – Forschungszentrum Jülich</h3>
        <ul>
            <li>Efficiency improvement of large stack electrolyzers</li>
        </ul>

        <h2>Education</h2>
        <ul>
            <li>PhD in Water Electrolysis, Aalborg University</li>
        </ul>

        <h2>Languages</h2>
        <ul>
            <li>English</li>
            <li>Danish</li>
        </ul>

        <h2>Technical Skills</h2>
        <ul>
            <li><strong>Process Simulation:</strong> HYSYS, FLARE, AutoCAD Plant</li>
            <li><strong>Safety & Standards:</strong> PED, ISO 22734, API 520/521</li>
            <li><strong>Programming:</strong> Excel VBA</li>
        </ul>
        </body></html>
        '''

        output = BytesIO()
        HTML(string=full_html, base_url="/mnt/data/").write_pdf(output)
        encoded_pdf = base64.b64encode(output.getvalue()).decode()

        return html.A("📄 Download Full CV (PDF)", href=f"data:application/pdf;base64,{encoded_pdf}",
                      download=f"cv_full.pdf", target="_blank")

    return app.server
