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
                Address: 9260 Gistrup, Denmark<br>
                Passport: Danish<br>
                Phone: +45-2678-2233<br>
                Email: ssl@G4iE.dk<br>
                CVR: 45118711</p>
            </div>
            <div class="photo">
                <img src="image1.jpg" alt="Saeed photo">
            </div>
        </div>

        <h2>Summary</h2>
        <p>As a consultant, I specialize in the preparation of high-quality Process Flow Diagrams (PFDs), Piping and Instrumentation Diagrams (P&IDs), and extracting lists (valves, instruments, components, etc.) using AutoCAD Plant. I am also actively engaged in developing heat and mass balances to support the design and optimization of various plant types, such as Power-to-X (PtX), Carbon Capture, Utilization and Storage (CCUS), Biogas and Power Plants.</p>

        <h2>Professional Experience</h2>
        <h3>Self-Employed</h3>
        <p>Nov. 2027 – present, G4iE ApS, Gistrup, Denmark</p>
        <ul>
            <li>Site inspection and due diligence of a dynamic power to ammonia plant in Denmark.</li>
            <li>Prepare PFD for a biogas plant in Belgium.</li>
            <li>Prepare PFD and P&ID for a biogas plant in the UK.</li>
            <li>Design MW scaled air-source heat pump plant.</li>
            <li>Developing innovative solutions within Power-to-X and CCUS.</li>
        </ul>

        <h3>Senior Specialist</h3>
        <p>Jan. 2023 – Sep. 2024, COWI, Aalborg, Denmark</p>
        <ul>
            <li>Process design for a 1GW hydrogen production plant, integrating PlugPower’s electrolysis modules.</li>
            <li>Developed PFDs, P&IDs, and designed vent systems for hydrogen and oxygen lines.</li>
            <li>Conducted feasibility studies for carbon capture and green hydrogen projects in Denmark.</li>
            <li>Performed ASPEN HYSYS calculations and sized safety equipment to API 520, 521.</li>
            <li>Updated “Technology Data for Carbon Capture, Transport and Storage” for Energistyrrelsen.</li>
            <li>Prepared PFD and simulation for a CCS plant.</li>
        </ul>

        <h3>PtX Senior Process Engineer - Owners Engineering</h3>
        <p>Jan. 2022 - Dec. 2022, Blue Power Partners, Aalborg, Denmark</p>
        <ul>
            <li>Feasibility studies and techno-economic assessments for green ammonia plants in Morocco and Chile.</li>
            <li>Designed plant layouts, developed CAPEX/OPEX models, and assessed LCoA.</li>
        </ul>

        <h3>Project Engineer</h3>
        <p>Feb. 2019 - Jan. 2022, Nature Energy A/S, Støvring, Denmark</p>
        <ul>
            <li>Detailed design of biogas plants: H&M balances, PFDs, P&IDs, 3D model reviews.</li>
            <li>Specified heat exchangers, pumps, and boilers.</li>
            <li>Pipe, valve, and pump selection (Grundfos, dosing, displacement types).</li>
            <li>Integrated 9 MW electrolyser and bio-trickling filters into biogas plant.</li>
            <li>Conducted risk assessments, troubleshooting, and optimization.</li>
        </ul>

        <h3>PhD Stipend</h3>
        <p>Jan. 2016 - Jan. 2019, Energy Technology Dep., Aalborg University</p>
        <ul>
            <li>Designed and tested PEM water electrolysis systems.</li>
            <li>Presented electrolysis research at international conferences.</li>
        </ul>

        <h3>Visiting Internship</h3>
        <p>Jul. 2017 - Dec. 2017, Forschungszentrum Jülich, Germany</p>
        <ul>
            <li>Contributed to large electrolyser stack design and efficiency improvement.</li>
        </ul>

        <h3>Researcher</h3>
        <p>2014 - 2016, Energy Technology Dep., Aalborg University</p>

        <h3>Consultant</h3>
        <p>2013 - 2014, R&R Consult, Aalborg, Denmark</p>

        <h2>Education</h2>
        <p>PhD in water electrolysis, Aalborg University, Jan. 2016 – Jan. 2019</p>

        <h2>Language</h2>
        <ul>
            <li>English</li>
            <li>Danish</li>
        </ul>

        <h2>Personal Competences</h2>
        <ul>
            <li>Self-motivated, result-oriented, and analytical.</li>
            <li>Strong-willed with a systematic approach to problem-solving.</li>
        </ul>

        <h2>Technical Skills</h2>
        <ul>
            <li><strong>Process Simulation and Design:</strong> ASPEN HYSYS, FLARE, PLUS, AutoCAD Plant.</li>
            <li><strong>Safety and Standards:</strong> PED, ISO 22734, API 520, 521.</li>
            <li><strong>Programming:</strong> Excel VBA for process calculations and modelling.</li>
        </ul>
        </body>
        </html>
        '''

        output = BytesIO()
        HTML(string=full_html, base_url="/mnt/data/").write_pdf(output)
        encoded_pdf = base64.b64encode(output.getvalue()).decode()

        return html.A("📄 Download Full CV (PDF)", href=f"data:application/pdf;base64,{encoded_pdf}",
                      download=f"cv_full.pdf", target="_blank")

    return app.server
