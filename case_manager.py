import sqlite3
from datetime import datetime

DB = "forensic.db"


def create_case(case_id,
                case_name,
                description,
                investigator,
                priority):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
    INSERT INTO cases(
        case_id,
        case_name,
        description,
        investigator,
        priority,
        status,
        created_at
    )
    VALUES(?,?,?,?,?,?,?)
    """,
    (
        case_id,
        case_name,
        description,
        investigator,
        priority,
        "Open",
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()

def get_cases():
    conn = sqlite3.connect(DB)
    cases = conn.execute("""
    SELECT *
    FROM cases
    ORDER BY created_at DESC
    """).fetchall()
    conn.close()
    return cases

def close_case(case_id):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
    UPDATE cases
    SET status='Closed'
    WHERE case_id=?
    """, (case_id,))
    conn.commit()
    conn.close()

def get_case(case_id):
    conn = sqlite3.connect(DB)
    case = conn.execute("""
    SELECT *
    FROM cases
    WHERE case_id=?
    """, (case_id,)).fetchone()
    conn.close()
    return case

def get_case_evidence(case_id):
    conn = sqlite3.connect(DB)
    evidence = conn.execute("""
    SELECT
        id,
        title,
        filename,
        uploaded_by,
        upload_time
    FROM evidence
    WHERE case_id=?
    ORDER BY upload_time DESC
    """, (case_id,)).fetchall()
    conn.close()
    return evidence

def get_case_alerts(case_id):
    conn = sqlite3.connect(DB)
    count = conn.execute("""
    SELECT COUNT(*)
    FROM tamper_alerts
    WHERE evidence_id IN (
        SELECT id
        FROM evidence
        WHERE case_id=?
    )
    """, (case_id,)).fetchone()[0]
    conn.close()
    return count

def get_case_statistics(case_id):
    conn = sqlite3.connect(DB)
    stats = {}
    stats["evidence"] = conn.execute("""
    SELECT COUNT(*)
    FROM evidence
    WHERE case_id=?
    """, (case_id,)).fetchone()[0]

    stats["verified"] = conn.execute("""
    SELECT COUNT(*)
    FROM verification_logs
    WHERE evidence_id IN (
        SELECT id
        FROM evidence
        WHERE case_id=?
    )
    AND status='Verified'
    """, (case_id,)).fetchone()[0]

    stats["tampered"] = conn.execute("""
    SELECT COUNT(*)
    FROM verification_logs
    WHERE evidence_id IN (
        SELECT id
        FROM evidence
        WHERE case_id=?
    )
    AND status='Tampered'
    """, (case_id,)).fetchone()[0]

    conn.close()
    return stats


def update_case(
    case_id,
    case_name,
    description,
    investigator,
    priority,
    status
):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
    UPDATE cases
    SET
        case_name=?,
        description=?,
        investigator=?,
        priority=?,
        status=?
    WHERE case_id=?
    """,
    (
        case_name,
        description,
        investigator,
        priority,
        status,
        case_id
    ))

    conn.commit()
    conn.close()

def delete_case(case_id):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute(
        "DELETE FROM cases WHERE case_id=?",
        (case_id,)
    )
    conn.commit()
    conn.close()

def get_case_statistics(case_id):

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    total = c.execute("""
    SELECT COUNT(*)
    FROM evidence
    WHERE case_id=?
    """,(case_id,)).fetchone()[0]

    verified = c.execute("""
    SELECT COUNT(*)
    FROM verification_logs
    WHERE status='Verified'
    AND evidence_id IN (
        SELECT id FROM evidence
        WHERE case_id=?
    )
    """,(case_id,)).fetchone()[0]

    tampered = c.execute("""
    SELECT COUNT(*)
    FROM verification_logs
    WHERE status='Tampered'
    AND evidence_id IN (
        SELECT id FROM evidence
        WHERE case_id=?
    )
    """,(case_id,)).fetchone()[0]

    alerts = c.execute("""
    SELECT COUNT(*)
    FROM tamper_alerts
    WHERE evidence_id IN(
        SELECT id
        FROM evidence
        WHERE case_id=?
    )
    """,(case_id,)).fetchone()[0]

    conn.close()

    return total, verified, tampered, alerts