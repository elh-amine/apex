import dash
from dash import dcc, html, Input, Output, dash_table
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import sys, os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import api_client as api

app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = "APEX — Floor Monitoring"

COLORS = {
    'bg': '#0D1421', 'card': '#162035', 'navy': '#0A2342',
    'navy_light': '#1565C0', 'red': '#C62828', 'red_light': '#EF5350',
    'amber': '#FF8F00', 'success': '#2E7D32', 'text': '#E8EDF5', 'muted': '#8899AA'
}

PLOTLY_TEMPLATE = dict(
    layout=go.Layout(
        paper_bgcolor=COLORS['card'],
        plot_bgcolor=COLORS['card'],
        font=dict(color=COLORS['text'], family='Inter'),
        xaxis=dict(gridcolor='rgba(255,255,255,0.07)'),
        yaxis=dict(gridcolor='rgba(255,255,255,0.07)'),
    )
)

app.layout = html.Div([
    html.Div([
        html.Span("▲ APEX", className="apex-logo"),
        html.Span("  Automotive Process EXcellence Platform",
                   style={'color': COLORS['muted'], 'marginLeft': '10px'})
    ], className="apex-header"),

    dcc.Tabs(id="main-tabs", value="tab-overview", children=[
        dcc.Tab(label="Line Overview", value="tab-overview", className="dash-tab", selected_className="dash-tab--selected"),
        dcc.Tab(label="Qualité / SPC", value="tab-spc", className="dash-tab", selected_className="dash-tab--selected"),
        dcc.Tab(label="ML Prédictif", value="tab-ml", className="dash-tab", selected_className="dash-tab--selected"),
        dcc.Tab(label="FMEA Live", value="tab-fmea", className="dash-tab", selected_className="dash-tab--selected"),
        dcc.Tab(label="Rapports", value="tab-reports", className="dash-tab", selected_className="dash-tab--selected"),
    ]),

    html.Div(id="tab-content", className="tab-content-wrapper"),

    dcc.Interval(id="interval-refresh", interval=10*1000, n_intervals=0)  # refresh toutes les 10s
])


# ============ ONGLET 1 — Line Overview ============

def render_overview():
    ftq = api.get_ftq()
    oee = api.get_oee()
    dpmo = api.get_dpmo()
    ppm_data = api.get_ppm()

    ppm_value = next((r['value'] for r in ppm_data if 'emboutissage' in r.get('kpi_name', '')), 0)

    return html.Div([
        html.Div([
            html.Div([
                html.Div("PPM Emboutissage", className="kpi-label"),
                html.Div(f"{ppm_value:,.0f}", className="kpi-value kpi-ppm"),
            ], className="card", style={'flex': 1}),

            html.Div([
                html.Div("FTQ", className="kpi-label"),
                html.Div(f"{ftq.get('ftq_percent', 0)}%", className="kpi-value kpi-ftq"),
            ], className="card", style={'flex': 1}),

            html.Div([
                html.Div("OEE", className="kpi-label"),
                html.Div(f"{oee.get('oee_percent', 0)}%", className="kpi-value kpi-oee"),
            ], className="card", style={'flex': 1}),

            html.Div([
                html.Div("Niveau Sigma", className="kpi-label"),
                html.Div(f"{dpmo.get('sigma_level', 0)}σ", className="kpi-value kpi-sigma"),
            ], className="card", style={'flex': 1}),
        ], style={'display': 'flex', 'gap': '1rem'}),

        html.Div([
            dcc.Graph(id="pareto-chart-overview")
        ], className="card"),
    ])


# ============ ONGLET 2 — Qualité / SPC ============

def render_spc():
    return html.Div([
        html.Div([
            html.Label("Feature à analyser :", style={'color': COLORS['muted']}),
            dcc.Dropdown(
                id="spc-feature-dropdown",
                options=[
                    {"label": "Surface du défaut (Pixels_Areas)", "value": "Pixels_Areas"},
                    {"label": "Luminosité totale (Sum_of_Luminosity)", "value": "Sum_of_Luminosity"},
                    {"label": "Périmètre X", "value": "X_Perimeter"},
                    {"label": "Index Orientation", "value": "Orientation_Index"},
                ],
                value="Pixels_Areas",
                style={'width': '400px', 'color': '#000'}
            ),
        ], className="card"),

        html.Div([
            dcc.Graph(id="spc-chart-graph")
        ], className="card"),

        html.Div(id="spc-violations-table", className="card"),
    ])


# ============ ONGLET 3 — ML Prédictif ============

def render_ml():
    return html.Div([
        html.Div([
            html.H4("Dernières alertes qualité (Module A/B)", style={'color': COLORS['text']}),
            html.Div(id="ml-scores-table")
        ], className="card"),

        html.Div([
            html.H4("Alertes équipement (Module C)", style={'color': COLORS['text']}),
            html.Div(id="equipment-alerts-table")
        ], className="card"),
    ])


# ============ ONGLET 4 — FMEA Live ============

def render_fmea():
    fmea_data = api.get_fmea()
    df_fmea = pd.DataFrame(fmea_data)

    if df_fmea.empty:
        return html.Div("Aucune donnée FMEA disponible.", className="card")

    return html.Div([
        dash_table.DataTable(
            data=df_fmea.to_dict('records'),
            columns=[{"name": c, "id": c} for c in df_fmea.columns],
            style_header={'backgroundColor': COLORS['navy'], 'color': 'white', 'fontWeight': 'bold'},
            style_cell={'backgroundColor': COLORS['card'], 'color': COLORS['text'], 'border': '1px solid rgba(255,255,255,0.07)'},
            style_data_conditional=[
                {'if': {'filter_query': '{rpn} > 100', 'column_id': 'rpn'},
                 'backgroundColor': COLORS['red'], 'color': 'white'},
                {'if': {'filter_query': '{rpn} >= 50 && {rpn} <= 100', 'column_id': 'rpn'},
                 'backgroundColor': COLORS['amber'], 'color': 'black'},
                {'if': {'filter_query': '{rpn} < 50', 'column_id': 'rpn'},
                 'backgroundColor': COLORS['success'], 'color': 'white'},
            ],
        )
    ], className="card")


# ============ ONGLET 5 — Rapports ============

def render_reports():
    bc = api.get_business_case(station=3)

    return html.Div([
        html.Div([
            html.H4("Générer des rapports", style={'color': COLORS['text']}),
            html.A(html.Button("📄 Générer rapport 8D", style={'marginRight': '1rem'}),
                   href="http://127.0.0.1:8000/quality-report", target="_blank"),
            html.A(html.Button("📋 Exporter Control Plan"),
                   href="http://127.0.0.1:8000/control-plan", target="_blank"),
        ], className="card"),

        html.Div([
            html.H4("Business Case — Économie par station de détection", style={'color': COLORS['text']}),
            html.Label("Station de détection :", style={'color': COLORS['muted']}),
            dcc.Slider(id="station-slider", min=1, max=8, step=1, value=3,
                       marks={i: str(i) for i in range(1, 9)}),
            html.Div(id="business-case-output", style={'marginTop': '1rem', 'fontSize': '1.2rem'})
        ], className="card"),
    ])


# ============ Callback principal — changement d'onglet ============

@app.callback(Output("tab-content", "children"), Input("main-tabs", "value"))
def render_tab(tab):
    if tab == "tab-overview":
        return render_overview()
    elif tab == "tab-spc":
        return render_spc()
    elif tab == "tab-ml":
        return render_ml()
    elif tab == "tab-fmea":
        return render_fmea()
    elif tab == "tab-reports":
        return render_reports()
    return html.Div("Onglet inconnu")


# ============ Callbacks — Overview ============

@app.callback(Output("pareto-chart-overview", "figure"), Input("interval-refresh", "n_intervals"))
def update_pareto_overview(n):
    data = api.get_pareto()
    df = pd.DataFrame(data)
    if df.empty:
        return go.Figure()

    fig = go.Figure()
    fig.add_bar(x=df['defect_type'], y=df['count'], marker_color=COLORS['red_light'], name="Fréquence")
    fig.add_scatter(x=df['defect_type'], y=df['cumulative_pct'], yaxis="y2",
                     mode='lines+markers', marker_color=COLORS['amber'], name="Cumul %")
    fig.update_layout(
        template=PLOTLY_TEMPLATE, title="Pareto des défauts — Ligne emboutissage",
        yaxis2=dict(overlaying='y', side='right', range=[0, 100], showgrid=False),
        height=400
    )
    return fig


# ============ Callbacks — SPC ============

@app.callback(
    Output("spc-chart-graph", "figure"),
    Output("spc-violations-table", "children"),
    Input("spc-feature-dropdown", "value")
)
def update_spc(feature):
    data = api.get_spc(feature)
    if not data or 'values_sample' not in data:
        return go.Figure(), html.Div("Aucune donnée")

    values = data['values_sample']
    mean, ucl, lcl = data['mean'], data['ucl'], data['lcl']

    fig = go.Figure()
    fig.add_scatter(y=values, mode='lines+markers', marker_color=COLORS['navy_light'], name=feature)
    fig.add_hline(y=mean, line_color=COLORS['success'], annotation_text="Moyenne")
    fig.add_hline(y=ucl, line_color=COLORS['red_light'], line_dash="dash", annotation_text="UCL")
    fig.add_hline(y=lcl, line_color=COLORS['red_light'], line_dash="dash", annotation_text="LCL")
    fig.update_layout(template=PLOTLY_TEMPLATE, title=f"Carte de contrôle SPC — {feature}", height=450)

    violations_text = html.Div([
        html.H5(f"Violations détectées : {data.get('n_violations', 0)}", style={'color': COLORS['red_light']}),
        html.P(f"Sur {data.get('n_points', 0)} points analysés", style={'color': COLORS['muted']})
    ])

    return fig, violations_text


# ============ Callbacks — ML ============

@app.callback(Output("ml-scores-table", "children"), Input("interval-refresh", "n_intervals"))
def update_ml_scores(n):
    data = api.get_ml_scores(limit=15)
    df = pd.DataFrame(data)
    if df.empty:
        return html.Div("Aucune donnée")

    cols = [c for c in ['timestamp', 'piece_id', 'process', 'defect_type_pred', 'gonogo_score', 'alert_level'] if c in df.columns]
    return dash_table.DataTable(
        data=df[cols].to_dict('records'),
        columns=[{"name": c, "id": c} for c in cols],
        style_header={'backgroundColor': COLORS['navy'], 'color': 'white'},
        style_cell={'backgroundColor': COLORS['card'], 'color': COLORS['text']},
        style_data_conditional=[
            {'if': {'filter_query': '{alert_level} = "critical"'}, 'backgroundColor': COLORS['red']},
            {'if': {'filter_query': '{alert_level} = "warning"'}, 'backgroundColor': COLORS['amber']},
        ],
        page_size=10
    )


@app.callback(Output("equipment-alerts-table", "children"), Input("interval-refresh", "n_intervals"))
def update_equipment_alerts(n):
    data = api.get_equipment_alerts(limit=15)
    df = pd.DataFrame(data)
    if df.empty:
        return html.Div("Aucune donnée")

    return dash_table.DataTable(
        data=df.to_dict('records'),
        columns=[{"name": c, "id": c} for c in df.columns],
        style_header={'backgroundColor': COLORS['navy'], 'color': 'white'},
        style_cell={'backgroundColor': COLORS['card'], 'color': COLORS['text']},
        style_data_conditional=[
            {'if': {'filter_query': '{alert_level} = "critical"'}, 'backgroundColor': COLORS['red']},
            {'if': {'filter_query': '{alert_level} = "warning"'}, 'backgroundColor': COLORS['amber']},
        ],
        page_size=10
    )


# ============ Callback — Business Case ============

@app.callback(Output("business-case-output", "children"), Input("station-slider", "value"))
def update_business_case(station):
    bc = api.get_business_case(station=station)
    if not bc:
        return "Erreur de calcul"

    return html.Div([
        html.P(f"Coût correction à cette station : {bc.get('cost_per_piece_at_station_mad', 0)} MAD/pièce"),
        html.P(f"Coût correction en fin de ligne : {bc.get('cost_per_piece_at_end_line_mad', 0)} MAD/pièce"),
        html.P(f"Économie estimée : {bc.get('savings_per_piece_mad', 0)} MAD/pièce", 
               style={'color': COLORS['success'], 'fontWeight': 'bold'}),
        html.P(f"Économie journalière estimée : {bc.get('estimated_daily_savings_mad', 0)} MAD/jour",
               style={'color': COLORS['success'], 'fontWeight': 'bold', 'fontSize': '1.4rem'}),
    ])


if __name__ == "__main__":
    app.run(debug=True, port=8050)