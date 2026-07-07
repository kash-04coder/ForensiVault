import sqlite3
import pandas as pd

DB = "forensic.db"


def get_evidence_details(evidence_id):

    conn = sqlite3.connect(DB)

    evidence = conn.execute("""
        SELECT *
        FROM evidence
        WHERE id=?
    """, (evidence_id,)).fetchone()

    custody = pd.read_sql_query("""
        SELECT *
        FROM custody
        WHERE evidence_id=?
        ORDER BY timestamp
    """, conn, params=(evidence_id,))

    verification = pd.read_sql_query("""
        SELECT *
        FROM verification_logs
        WHERE evidence_id=?
        ORDER BY verification_time DESC
    """, conn, params=(evidence_id,))

    alerts = pd.read_sql_query("""
        SELECT *
        FROM tamper_alerts
        WHERE evidence_id=?
        ORDER BY detection_time DESC
    """, conn, params=(evidence_id,))

    conn.close()

    return evidence, custody, verification, alerts