import requests

API_BASE = "http://127.0.0.1:8000"

def safe_get(endpoint, params=None, default=None):
    try:
        resp = requests.get(f"{API_BASE}{endpoint}", params=params, timeout=5)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"Erreur API {endpoint}: {e}")
        return default if default is not None else {}

def get_ppm():
    return safe_get("/ppm", default=[])

def get_ftq():
    return safe_get("/ftq", default={"ftq_percent": 0})

def get_oee():
    return safe_get("/oee", default={"oee_percent": 0})

def get_dpmo():
    return safe_get("/dpmo", default={"dpmo": 0, "sigma_level": 0})

def get_pareto():
    return safe_get("/pareto-defects", default=[])

def get_spc(feature="Pixels_Areas"):
    return safe_get(f"/spc-chart/{feature}", default={})

def get_fmea():
    return safe_get("/fmea", default=[])

def get_ml_scores(limit=20):
    return safe_get("/ml-scores", params={"limit": limit}, default=[])

def get_equipment_alerts(limit=20):
    return safe_get("/equipment-alerts", params={"limit": limit}, default=[])

def get_business_case(station=3):
    return safe_get("/business-case", params={"station": station}, default={})