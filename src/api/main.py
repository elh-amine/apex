from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Dict
import sqlite3
import pandas as pd
import numpy as np
import joblib
import os
from datetime import datetime
from scipy.stats import norm
from ucimlrepo import fetch_ucirepo
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

app = FastAPI(title="APEX API", description="Automotive Process EXcellence Platform")

DB_PATH = "../../apex.db"
MODELS_DIR = "../../models"
REPORTS_DIR = "../../reports"

# ============ Schémas Pydantic ============

class DefectFeatures(BaseModel):
    X_Minimum: float
    X_Maximum: float
    Y_Minimum: float
    Y_Maximum: float
    Pixels_Areas: float
    X_Perimeter: float
    Y_Perimeter: float
    Sum_of_Luminosity: float
    Minimum_of_Luminosity: float
    Maximum_of_Luminosity: float
    Length_of_Conveyer: float
    TypeOfSteel_A300: float
    TypeOfSteel_A400: float
    Steel_Plate_Thickness: float
    Edges_Index: float
    Empty_Index: float
    Square_Index: float
    Outside_X_Index: float
    Edges_X_Index: float
    Edges_Y_Index: float
    Outside_Global_Index: float
    LogOfAreas: float
    Log_X_Index: float
    Log_Y_Index: float
    Orientation_Index: float
    Luminosity_Index: float
    SigmoidOfAreas: float

class GoNoGoFeatures(BaseModel):
    features: Dict[str, float]

# ============ Chargement des modèles au démarrage ============

model_a = joblib.load(f"{MODELS_DIR}/module_a_defect_classifier.pkl")
scaler_a = joblib.load(f"{MODELS_DIR}/module_a_scaler.pkl")

model_b = joblib.load(f"{MODELS_DIR}/module_b_gonogo_classifier.pkl")
top_features_b = joblib.load(f"{MODELS_DIR}/module_b_selected_features.pkl")
threshold_b = joblib.load(f"{MODELS_DIR}/module_b_optimal_threshold.pkl")

_steel_cache = fetch_ucirepo(id=198)
STEEL_X = _steel_cache.data.features
STEEL_Y = _steel_cache.data.targets.idxmax(axis=1)

def get_connection():
    return sqlite3.connect(DB_PATH)

# ============ Génération PDF (fonctions internes) ============

styles = getSampleStyleSheet()
title_style = ParagraphStyle('APEXTitle', parent=styles['Heading1'], textColor=colors.HexColor('#0A2342'))
section_style = ParagraphStyle('APEXSection', parent=styles['Heading2'], textColor=colors.HexColor('#C62828'))

def generate_8d_report(filepath: str, defect_summary: dict):
    doc = SimpleDocTemplate(filepath, pagesize=A4)
    elements = []
    elements.append(Paragraph("APEX — Rapport 8D", title_style))
    elements.append(Paragraph(f"Généré le {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
    elements.append(Spacer(1, 1*cm))

    disciplines = [
        ("D1 — Équipe", "Responsable Qualité, Ingénieur Process, Opérateur ligne emboutissage, Responsable Maintenance"),
        ("D2 — Description du problème",
         f"Défaut prioritaire identifié : {defect_summary.get('top_defect', 'N/A')} — "
         f"{defect_summary.get('top_defect_count', 'N/A')} occurrences détectées sur la ligne emboutissage."),
        ("D3 — Actions conservatoires",
         "Renforcement du contrôle visuel à 100% en sortie de presse jusqu'à identification de la cause racine."),
        ("D4 — Analyse des causes racines",
         "Cf. diagramme Ishikawa (branche Machine dominante) et Pareto des défauts. "
         "Feature la plus discriminante identifiée par le modèle ML : LogOfAreas (taille du défaut)."),
        ("D5 — Actions correctives",
         "Ajustement des paramètres de la presse (vitesse, force). Contrôle renforcé du lot matière."),
        ("D6 — Vérification de l'efficacité",
         "Suivi du PPM sur 30 jours post-action. Objectif : réduction de 30% du taux de défaut prioritaire."),
        ("D7 — Actions préventives",
         "Intégration du modèle ML de classification des défauts en contrôle continu."),
        ("D8 — Félicitations à l'équipe",
         "Clôture du 8D après vérification de l'efficacité des actions correctives sur 30 jours."),
    ]

    for titre, contenu in disciplines:
        elements.append(Paragraph(titre, section_style))
        elements.append(Paragraph(contenu, styles['Normal']))
        elements.append(Spacer(1, 0.5*cm))

    doc.build(elements)


def generate_control_plan(filepath: str):
    doc = SimpleDocTemplate(filepath, pagesize=A4)
    elements = []
    elements.append(Paragraph("APEX — Control Plan", title_style))
    elements.append(Paragraph(f"Généré le {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
    elements.append(Spacer(1, 1*cm))

    data = [
        ["Caractéristique", "Méthode", "Fréquence", "Échantillon", "Nominal", "Tolérance", "Action"],
        ["Surface défaut", "Vision industrielle", "100%", "1 pièce", "< 500 px", "±20%", "Blocage + inspection"],
        ["Type acier", "Certificat matière", "Par lot", "1 lot", "A300/A400", "Conforme fiche", "Retour fournisseur"],
        ["Couple presse", "Capteur presse", "Continu", "1 cycle", "Cible process", "±5%", "Arrêt ligne + réglage"],
        ["Vitesse rotation", "Capteur moteur", "Continu", "1 cycle", "Cible process", "±5%", "Arrêt ligne + réglage"],
        ["Score go/no-go ML", "Modèle prédictif", "100%", "1 pièce", "< seuil alerte", "N/A", "Déroutement pièce"],
    ]

    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0A2342')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F0F0F0')]),
    ]))
    elements.append(table)
    doc.build(elements)

# ============ Endpoints ============

@app.get("/")
def root():
    return {"message": "APEX API — Automotive Process EXcellence Platform"}


@app.get("/stream-line")
def stream_line(limit: int = 20):
    conn = get_connection()
    df = pd.read_sql(f"SELECT * FROM ml_quality_scores ORDER BY timestamp DESC LIMIT {limit}", conn)
    conn.close()
    return df.to_dict(orient="records")


@app.get("/ppm")
def get_ppm():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM dmaic_results WHERE kpi_name LIKE '%PPM%'", conn)
    conn.close()
    return df.to_dict(orient="records")


@app.get("/ftq")
def get_ftq():
    conn = get_connection()
    total = pd.read_sql("SELECT COUNT(*) as n FROM raw_inspections", conn)['n'][0]
    conformes = pd.read_sql("SELECT COUNT(*) as n FROM raw_inspections WHERE conformite = 1", conn)['n'][0]
    conn.close()
    ftq = (conformes / total * 100) if total > 0 else 0
    return {"ftq_percent": round(ftq, 2), "total_pieces": int(total), "conformes": int(conformes)}


@app.get("/oee")
def get_oee(availability: float = 0.92, performance: float = 0.87):
    ftq_data = get_ftq()
    quality = ftq_data['ftq_percent'] / 100
    oee = availability * performance * quality
    return {
        "oee_percent": round(oee * 100, 2),
        "availability": availability,
        "performance": performance,
        "quality": round(quality * 100, 2),
        "note": "Availability/Performance simulés, Quality basé sur FTQ réel"
    }


@app.get("/dpmo")
def get_dpmo():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM dmaic_results WHERE kpi_name = 'DPMO_assemblage'", conn)
    conn.close()
    if df.empty:
        raise HTTPException(404, "DPMO non trouvé")
    row = df.iloc[0]
    return {
        "dpmo": row['value'],
        "sigma_level": round(row['sigma_level'], 2),
        "target": row['target'],
        "status": row['status']
    }


@app.get("/pareto-defects")
def get_pareto():
    conn = get_connection()
    df = pd.read_sql(
        "SELECT defect_type, COUNT(*) as count FROM raw_inspections GROUP BY defect_type ORDER BY count DESC",
        conn
    )
    conn.close()
    df['cumulative_pct'] = (df['count'].cumsum() / df['count'].sum() * 100).round(2)
    return df.to_dict(orient="records")


@app.get("/spc-chart/{feature}")
def spc_chart(feature: str):
    if feature not in STEEL_X.columns:
        raise HTTPException(400, f"Feature inconnue. Choix possibles: {list(STEEL_X.columns)}")

    values = STEEL_X[feature]
    mean = values.mean()
    std = values.std()
    ucl = mean + 3*std
    lcl = mean - 3*std

    violations = []
    for i, v in enumerate(values):
        if v > ucl or v < lcl:
            violations.append({"index": int(i), "value": float(v), "rule": "WE Rule 1 - hors limites 3-sigma"})

    return {
        "feature": feature,
        "mean": round(mean, 4),
        "ucl": round(ucl, 4),
        "lcl": round(lcl, 4),
        "n_points": len(values),
        "n_violations": len(violations),
        "violations": violations[:20],
        "values_sample": values.head(100).tolist()
    }


@app.get("/fmea")
def get_fmea():
    return [
        {"fonction": "Emboutissage panneau carrosserie", "mode_defaillance": "Rayure profonde (K_Scratch)",
         "effet": "Rejet pièce, retouche coûteuse", "cause": "Usure outillage / frottement convoyeur",
         "occurrence": 6, "severite": 7, "detectabilite": 3, "rpn": 126,
         "action_corrective": "Contrôle usure outillage renforcé", "rpn_apres_action": 42},
        {"fonction": "Emboutissage panneau carrosserie", "mode_defaillance": "Bosse / déformation (Bumps)",
         "effet": "Non-conformité esthétique", "cause": "Réglage incorrect de la presse",
         "occurrence": 5, "severite": 6, "detectabilite": 4, "rpn": 120,
         "action_corrective": "Vérification SPC des paramètres presse", "rpn_apres_action": 40},
        {"fonction": "Emboutissage panneau carrosserie", "mode_defaillance": "Rayure fine (Z_Scratch)",
         "effet": "Non-conformité esthétique mineure", "cause": "Manipulation / transport interne",
         "occurrence": 4, "severite": 4, "detectabilite": 3, "rpn": 48,
         "action_corrective": "Formation manipulation opérateurs", "rpn_apres_action": 24}
    ]


@app.post("/predict-defect")
def predict_defect(data: DefectFeatures):
    X_input = pd.DataFrame([data.dict()])
    # Réordonne les colonnes exactement comme lors de l'entraînement du scaler
    X_input = X_input[scaler_a.feature_names_in_]
    X_scaled = scaler_a.transform(X_input)
    prediction = model_a.predict(X_scaled)[0]
    proba = model_a.predict_proba(X_scaled)[0].max()
    return {"defect_type_predicted": prediction, "confidence_score": round(float(proba), 4)}


@app.post("/go-nogo")
def go_nogo(data: GoNoGoFeatures):
    row = {feat: data.features.get(feat, 0.0) for feat in top_features_b}
    X_input = pd.DataFrame([row])[top_features_b]
    score = model_b.predict_proba(X_input)[0][1]

    if score > threshold_b:
        alert = "critical"
    elif score > threshold_b * 0.6:
        alert = "warning"
    else:
        alert = "ok"

    return {
        "gonogo_score": round(float(score), 4),
        "threshold_used": round(float(threshold_b), 4),
        "alert_level": alert
    }


@app.get("/ml-scores")
def get_ml_scores(limit: int = 50):
    conn = get_connection()
    df = pd.read_sql(f"SELECT * FROM ml_quality_scores ORDER BY timestamp DESC LIMIT {limit}", conn)
    conn.close()
    return df.to_dict(orient="records")


@app.get("/equipment-alerts")
def get_equipment_alerts(limit: int = 50):
    conn = get_connection()
    df = pd.read_sql(f"SELECT * FROM equipment_alerts ORDER BY timestamp DESC LIMIT {limit}", conn)
    conn.close()
    return df.to_dict(orient="records")


@app.get("/quality-report")
def quality_report():
    os.makedirs(REPORTS_DIR, exist_ok=True)
    conn = get_connection()
    pareto = pd.read_sql(
        """SELECT defect_type, COUNT(*) as count FROM raw_inspections 
           WHERE defect_type != 'Other_Faults'
           GROUP BY defect_type ORDER BY count DESC LIMIT 1""",
        conn
    )
    conn.close()
    summary = {
        "top_defect": pareto.iloc[0]['defect_type'] if not pareto.empty else "N/A",
        "top_defect_count": int(pareto.iloc[0]['count']) if not pareto.empty else "N/A"
    }
    filepath = f"{REPORTS_DIR}/rapport_8D_apex.pdf"
    generate_8d_report(filepath, summary)
    return FileResponse(filepath, filename="rapport_8D_apex.pdf", media_type="application/pdf")

@app.get("/control-plan")
def control_plan():
    os.makedirs(REPORTS_DIR, exist_ok=True)
    filepath = f"{REPORTS_DIR}/control_plan_apex.pdf"
    generate_control_plan(filepath)
    return FileResponse(filepath, filename="control_plan_apex.pdf", media_type="application/pdf")


@app.get("/business-case")
def business_case(station: int = 3, total_stations: int = 8,
                   cost_base: float = 50.0, pieces_per_day: int = 1000):
    cost_at_station = cost_base * (10 ** (station / total_stations))
    cost_at_end = cost_base * 10
    savings_per_piece = cost_at_end - cost_at_station
    daily_savings = savings_per_piece * pieces_per_day * 0.01

    return {
        "station": station,
        "cost_per_piece_at_station_mad": round(cost_at_station, 2),
        "cost_per_piece_at_end_line_mad": round(cost_at_end, 2),
        "savings_per_piece_mad": round(savings_per_piece, 2),
        "estimated_daily_savings_mad": round(daily_savings, 2),
        "assumption": "Coût de correction x10 entre début et fin de ligne (hypothèse fiche projet)"
    }