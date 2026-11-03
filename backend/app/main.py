from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from typing import Optional, List
import io
import sqlite3
from datetime import datetime
import pandas as pd

app = FastAPI(
    title="CMF & Operational Risk AI Governance Platform",
    version="1.0.0-ENTERPRISE",
    description="Plataforma Multi-Agente de Gobierno, Cumplimiento Normativo CMF (Ley 20.009) y Trazabilidad Operacional"
)

# Inicialización de la base de datos relacional para trazabilidad CMF
def init_db():
    conn = sqlite3.connect("cmf_audit_governance.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cmf_claims (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            claim_id TEXT,
            rut_client TEXT,
            claim_type TEXT,
            disputed_amount REAL,
            legal_deadline_days INT,
            risk_classification TEXT,
            recommended_action TEXT,
            ai_legal_summary TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.get("/")
def root():
    return {"status": "ACTIVE", "platform": "Banco de Chile CMF AI Governance Core"}

@app.post("/api/v1/governance/process-cmf-claim")
async def process_cmf_claim(
    claim_id: str = Form(...),
    rut_client: str = Form(...),
    claim_type: str = Form(...), # ej: FRAUDE_TRANSFERENCIA, COBRO_INDEBIDO, TARJETA_CLONADA
    disputed_amount: float = Form(...),
    evidence_file: UploadFile = File(None)
):
    clean_rut = rut_client.replace(".", "").replace("-", "").strip().upper()
    red_flags = []
    
    # --- AGENTE 1 & 2: REGLAS Y EVALUACIÓN DE FRAUDE (Ley 20.009 CMF) ---
    # En Chile, por Ley de Fraudes, montos bajo 35 UF (~$1.3M CLP) requieren restitución rápida si no hay culpa grave
    is_low_threshold = disputed_amount <= 1350000 
    
    if disputed_amount > 5000000:
        red_flags.append("Monto elevado en disputa: requiere revisión por Comité de Riesgo Operacional.")
    
    evidence_found = False
    if evidence_file and evidence_file.filename:
        evidence_found = True

    # --- AGENTE 3: SINTETIZADOR DE CUMPLIMIENTO LEGAL ---
    if claim_type.upper() in ["FRAUDE_TRANSFERENCIA", "TARJETA_CLONADA"] and is_low_threshold:
        risk_class = "MEDIO"
        action = "ABONO_PROVISORIO_AUTOMATICO"
        legal_summary = f"Aplica cobertura rápida según protocolo Ley 20.009 para el caso {claim_id}. Se emite orden de abono provisorio por ${disputed_amount:,.0f}."
        deadline_days = 5
    elif len(red_flags) > 0:
        risk_class = "ALTO"
        action = "DERIVAR_INVESTIGACION_FRAUDE"
        legal_summary = f"Caso {claim_id} presenta banderas rojas operacionales. Se pausa abono automático y se deriva a la Fiscalía Interna."
        deadline_days = 10
    else:
        risk_class = "BAJO"
        action = "RESOLUCION_FAVORABLE_STANDARD"
        legal_summary = f"Caso procesado sin discrepancias. Cumple con los criterios de atención normativos CMF."
        deadline_days = 7

    # --- PERSISTENCIA Y TRAZABILIDAD SQL ACID ---
    conn = sqlite3.connect("cmf_audit_governance.db")
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO cmf_claims 
        (timestamp, claim_id, rut_client, claim_type, disputed_amount, legal_deadline_days, risk_classification, recommended_action, ai_legal_summary)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        datetime.now().isoformat(), claim_id, clean_rut, claim_type, disputed_amount, 
        deadline_days, risk_class, action, legal_summary
    ))
    conn.commit()
    conn.close()

    return {
        "governance_status": "PROCESSED",
        "case_data": {
            "claim_id": claim_id,
            "rut_client": clean_rut,
            "claim_type": claim_type,
            "disputed_amount": disputed_amount
        },
        "cmf_compliance": {
            "risk_classification": risk_class,
            "recommended_action": action,
            "max_legal_deadline_days": deadline_days,
            "evidence_attached": evidence_found,
            "red_flags": red_flags
        },
        "ai_resolution_draft": legal_summary
    }

@app.get("/api/v1/governance/cmf-dashboard-metrics")
def get_cmf_metrics():
    """ Endpoint consumible por Power BI o Power Apps para tableros ejecutivos """
    conn = sqlite3.connect("cmf_audit_governance.db")
    df = pd.read_sql_query("SELECT * FROM cmf_claims ORDER BY id DESC LIMIT 100", conn)
    conn.close()
    
    if df.empty:
        return {"total_claims": 0, "records": []}
        
    metrics = {
        "total_claims": len(df),
        "high_risk_cases": len(df[df['risk_classification'] == 'ALTO']),
        "automatic_refunds": len(df[df['recommended_action'] == 'ABONO_PROVISORIO_AUTOMATICO']),
        "records": df.to_dict(orient="records")
    }
    return metrics
