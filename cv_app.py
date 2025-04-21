# cv_generator_app.py (modular Dash app for Flask server, PDF output)
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

        keep_phrases = {
            "biogas": ["biogas", "methane", "Nature Energy"],
            "hydrogen": ["hydrogen", "electrolysis", "electrolyser", "PEM", "HYSYS", "PlugPower"],
            "ptx": ["Power-to-X", "PtX", "green ammonia", "LCoA", "Blue Power"]
        }

        # Full HTML content with filtering support
        html_template = '''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Saeed S. Lafmejani – CV</title>
            <style>
                body {
                    font-family: 'Segoe UI', sans-serif;
                    margin: 0;
                    padding: 2rem;
                    line-height: 1.5;
                    color: #222;
                }
                .header {
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    border-bottom: 2px solid #aaa;
                    padding-bottom: 1rem;
                    margin-bottom: 2rem;
                }
                .profile-info {
                    max-width: 65%;
                }
                .profile-info h1 {
                    margin: 0;
                    font-size: 1.8rem;
                }
                .contact {
                    font-size: 0.9rem;
                }
                .photo img {
                    width: 100px;
                    border-radius: 8px;
                }
                h2 {
                    border-bottom: 1px solid #ccc;
                    margin-top: 2rem;
                    padding-bottom: 0.25rem;
                    font-size: 1.2rem;
                    color: #004080;
                }
                ul {
                    padding-left: 1.2rem;
                }
                .section {
                    margin-bottom: 1.5rem;
                }
            </style>
        </head>
        <body>

        <div class="header">
            <div class="profile-info">
                <h1>Saeed S. Lafmejani</h1>
                <p class="contact">
                    <strong>Role:</strong> Process / Project Engineer<br>
                    <strong>Address:</strong> 9260 Gistrup, Denmark<br>
                    <strong>Phone:</strong> +45 2678 2233<br>
                    <strong>Email:</strong> ssl@G4iE.dk<br>
                    <strong>CVR:</strong> 45118711<br>
                    <strong>Passport:</strong> Danish
                </p>
            </div>
            <div class="photo">
                <img src="image1.jpg" alt="Saeed Photo">
            </div>
        </div>

        <div class="section">
            <h2>Summary</h2>
            <p>Consultant specialized in Process Flow Diagrams (PFDs), P&IDs, and detailed plant design for PtX, CCUS, Biogas and Power Plants using AutoCAD Plant and Excel-based HMB tools. </p>
        </div>

        <div class="section">
            <h2>Professional Experience</h2>
            <ul>
                {jobs}
            </ul>
        </div>

        <div class="section">
            <h2>Education</h2>
            <ul>
                <li>PhD in Water Electrolysis – Aalborg University (2016–2019)</li>
            </ul>
        </div>

        <div class="section">
            <h2>Languages</h2>
            <ul>
                <li>English</li>
                <li>Danish</li>
            </ul>
        </div>

        <div class="section">
            <h2>Technical Skills</h2>
            <ul>
                <li><strong>Process Design:</strong> ASPEN HYSYS, AutoCAD Plant</li>
                <li><strong>Standards:</strong> PED, ISO 22734, API 520/521</li>
                <li><strong>Programming:</strong> Excel VBA</li>
            </ul>
        </div>

        </body>
        </html>
        '''

        job_data = [
            ("G4iE", "Due diligence of a power-to-ammonia plant in Denmark", "biogas,ptx"),
            ("G4iE", "PFD & P&ID design for biogas plants in Belgium & UK", "biogas"),
            ("G4iE", "MW-scale air-source heat pump system design", "ptx"),
            ("COWI", "Process design of a 1GW hydrogen production plant", "hydrogen,ptx"),
            ("COWI", "Feasibility studies for hydrogen/CCUS projects", "hydrogen,ptx"),
            ("COWI", "HYSYS simulations, safety system design per API standards", "hydrogen"),
            ("Blue Power Partners", "Feasibility of green ammonia in Morocco & Chile", "ptx"),
            ("Blue Power Partners", "LCoA and techno-economic assessments", "ptx"),
            ("Nature Energy", "Process design & optimization of biogas plants", "biogas"),
            ("Nature Energy", "Specification and selection of pumps, heat exchangers", "biogas")
        ]

        job_lines = []
        for company, desc, tags in job_data:
            if domain == "all" or domain in tags:
                job_lines.append(f"<li><strong>{company}:</strong> {desc}</li>")

        html_filled = html_template.replace("{jobs}", "\n".join(job_lines))
        output = BytesIO()
        HTML(string=html_filled).write_pdf(output)
        encoded_pdf = base64.b64encode(output.getvalue()).decode()

        return html.A("📄 Download CV (PDF)", href=f"data:application/pdf;base64,{encoded_pdf}",
                      download=f"cv_{domain}.pdf", target="_blank")

    return app.server
