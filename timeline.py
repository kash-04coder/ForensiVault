import sqlite3
import pandas as pd

DB = "forensic.db"

def get_timeline(evidence_id):

    conn = sqlite3.connect(DB)

    events = []

    # Evidence Registration
    evidence = conn.execute("""
        SELECT
            uploaded_by,
            upload_time,
            title
        FROM evidence
        WHERE id=?
    """, (evidence_id,)).fetchone()

    if evidence:
        events.append({
            "time": evidence[1],
            "user": evidence[0],
            "event": "Evidence Registered",
            "icon": "📁",
            "color": "green"
        })

    # Chain of Custody
    custody = conn.execute("""
        SELECT
            action,
            person,
            timestamp
        FROM custody
        WHERE evidence_id=?
    """, (evidence_id,)).fetchall()

    for row in custody:
        events.append({
            "time": row[2],
            "user": row[1],
            "event": row[0],
            "icon": "📜",
            "color": "blue"
        })

    # Verification Logs
    verification = conn.execute("""
        SELECT
            status,
            verified_by,
            verification_time
        FROM verification_logs
        WHERE evidence_id=?
    """, (evidence_id,)).fetchall()

    for row in verification:

        if row[0] == "Verified":

            icon = "✅"
            color = "green"

        else:

            icon = "🚨"
            color = "red"

        events.append({
            "time": row[2],
            "user": row[1],
            "event": row[0],
            "icon": icon,
            "color": color
        })

    # Tamper Alerts
    alerts = conn.execute("""
        SELECT
            detected_by,
            detection_time
        FROM tamper_alerts
        WHERE evidence_id=?
    """, (evidence_id,)).fetchall()

    for row in alerts:

        events.append({
            "time": row[1],
            "user": row[0],
            "event": "Tamper Alert Created",
            "icon": "⚠",
            "color": "orange"
        })

    conn.close()

    df = pd.DataFrame(events)

    df["time"] = pd.to_datetime(df["time"])

    df = df.sort_values("time")

    return df