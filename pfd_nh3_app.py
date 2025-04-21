import dash
from dash import dcc, html
import plotly.graph_objects as go

"""
PtA Block‑Flow Diagram (BFD) rendered with Dash + Plotly
─────────────────────────────────────────────────────────
• Flask backend with flask‑cors enabled
• Bootstrap CSS pulled via CDN (no Python imports)
• Dash graph mode‑bar disabled as requested
• All shapes/arrows are defined explicitly so you can
  tweak coordinates later if you want to refine the layout
  ─ just change the tuples in the `blocks` dict or add more
  arrows in the `flows` list.
"""

external_stylesheets = [
    "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css",
]
def init_pfd_nh3(server):
    app = dash.Dash(
        __name__,
        server=server,
        external_stylesheets=external_stylesheets,
        url_base_pathname='/pfd_nh3/',
        suppress_callback_exceptions=True,
    )

    # ── Helper: add rectangles & labels ────────────────────

    def add_block(fig, name, coords, fill="LightSkyBlue", line="RoyalBlue"):
        x0, y0, x1, y1 = coords
        cx = (x0 + x1) / 2
        cy = (y0 + y1) / 2
        fig.add_shape(type="rect", x0=x0, y0=y0, x1=x1, y1=y1,
                    line=dict(color=line), fillcolor=fill)
        fig.add_annotation(x=cx, y=cy, text=name, showarrow=False,
                        font=dict(size=10))


    def add_arrow(fig, src, dst, blocks):
        """Draw arrow between centre of block *src* → *dst*"""
        xs, ys = _centre(blocks[src])
        xd, yd = _centre(blocks[dst])
        fig.add_annotation(x=xd, y=yd, ax=xs, ay=ys,
                        xref="x", yref="y", axref="x", ayref="y",
                        showarrow=True, arrowhead=3, arrowsize=1)


    def _centre(coords):
        x0, y0, x1, y1 = coords
        return (x0 + x1) / 2, (y0 + y1) / 2


    # ── Define blocks (rough coordinates) ──────────────────
    blocks = {
        "Renewable Energy": (0.5, 8.0, 2.5, 9.0),
        "Transformer":      (3.0, 7.0, 4.7, 8.0),
        "Electrolyser":     (6.0, 7.0, 8.2, 8.0),
        "Municipality Water": (0.5, 5.5, 2.8, 6.5),
        "Hydrogen":         (9.0, 7.0, 10.7, 8.0),
        "O2 Vent":          (9.0, 8.5, 10.7, 9.5),
        "Air Compressor":   (0.5, 3.5, 2.8, 4.5),
        "Air Dryer":        (3.0, 3.5, 4.7, 4.5),
        "PSA":              (6.0, 3.5, 7.7, 4.5),
        "Nitrogen":         (8.8, 3.6, 9.8, 4.4),
        "Mixer":            (10.5, 6.5, 12.0, 7.5),
        "Main Compressor":  (13.0, 6.5, 15.0, 7.5),
        "Syngas":           (16.0, 6.8, 17.6, 7.2),
        "Ammonia Reactor":  (18.0, 6.0, 20.0, 8.0),
        "Separator":        (18.0, 4.4, 20.0, 5.4),
        "NH3 Storage":      (21.0, 4.4, 23.0, 5.4),
        "Recycle Loop":     (16.0, 4.4, 17.6, 5.4),
        "Booster Compressor": (14.5, 4.4, 15.8, 5.4),
        "Purge Recovery":   (18.0, 2.5, 20.0, 3.5),
        "Flare":            (21.0, 2.5, 22.8, 3.5),
        "H2 Scrubber":      (9.0, 5.5, 10.7, 6.5),
        "Deoxidiser+HX":    (11.0, 5.5, 12.7, 6.5),
        "Instrument Air":   (3.0, 1.8, 5.0, 2.8),
    }

    # ── Define flows (edges) ──────────────────────────────
    flows = [
        ("Renewable Energy", "Transformer"),
        ("Transformer", "Electrolyser"),
        ("Municipality Water", "Electrolyser"),
        ("Electrolyser", "Hydrogen"),
        ("Electrolyser", "O2 Vent"),
        ("Air Compressor", "Air Dryer"),
        ("Air Dryer", "PSA"),
        ("PSA", "Nitrogen"),
        ("Nitrogen", "Mixer"),
        ("Hydrogen", "H2 Scrubber"),
        ("H2 Scrubber", "Deoxidiser+HX"),
        ("Deoxidiser+HX", "Mixer"),
        ("Mixer", "Main Compressor"),
        ("Main Compressor", "Syngas"),
        ("Syngas", "Ammonia Reactor"),
        ("Ammonia Reactor", "Separator"),
        ("Separator", "NH3 Storage"),
        ("Separator", "Recycle Loop"),
        ("Recycle Loop", "Booster Compressor"),
        ("Booster Compressor", "Mixer"),
        ("Separator", "Purge Recovery"),
        ("Purge Recovery", "Flare"),
    ]

    # ── Build figure ──────────────────────────────────────
    fig = go.Figure()

    for name, box in blocks.items():
        add_block(fig, name, box)

    for src, dst in flows:
        add_arrow(fig, src, dst, blocks)

    fig.update_layout(
        xaxis=dict(visible=False, range=[0, 24]),
        yaxis=dict(visible=False, range=[0, 10]),
        plot_bgcolor="white",
        margin=dict(l=20, r=20, t=20, b=20),
        height=600,
    )

    # ── Dash Layout ───────────────────────────────────────
    app.layout = html.Div(
        [
            html.H3("PtA Block‑Flow Diagram", className="text-center my-3"),
            dcc.Graph(id="pta-bfd", figure=fig, config={"displayModeBar": False}),
        ],
        className="container-fluid",
    )
