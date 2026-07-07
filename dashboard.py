import sqlite3
import pandas as pd

DB = "forensic.db"


def get_dashboard_data():

    conn = sqlite3.connect(DB)

    data = {}

    data["evidence"] = conn.execute(
        "SELECT COUNT(*) FROM evidence"
    ).fetchone()[0]

    data["users"] = conn.execute(
        "SELECT COUNT(*) FROM users"
    ).fetchone()[0]

    data["alerts"] = conn.execute(
        """
        SELECT COUNT(*)
        FROM tamper_alerts
        WHERE status='Active'
        """
    ).fetchone()[0]

    data["verified"] = conn.execute(
        """
        SELECT COUNT(*)
        FROM verification_logs
        WHERE status='Verified'
        """
    ).fetchone()[0]

    data["tampered"] = conn.execute(
        """
        SELECT COUNT(*)
        FROM verification_logs
        WHERE status='Tampered'
        """
    ).fetchone()[0]

    uploads = pd.read_sql_query(
        """
        SELECT upload_time
        FROM evidence
        """,
        conn
    )

    roles = pd.read_sql_query(
        """
        SELECT role,COUNT(*) AS count
        FROM users
        GROUP BY role
        """,
        conn
    )

    activity = pd.read_sql_query(
        """
        SELECT username,
               action,
               timestamp
        FROM audit_logs
        ORDER BY timestamp DESC
        LIMIT 10
        """,
        conn
    )

    conn.close()

    return data, uploads, roles, activity