import sqlite3

def init_db():
    conn = sqlite3.connect(
        "forensic.db",
        timeout=10
    )
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS custody(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        evidence_id INTEGER,
        action TEXT,
        person TEXT,
        timestamp TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS evidence(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id TEXT,
    title TEXT,
    filename TEXT,
    filepath TEXT,
    encrypted_path TEXT,
    sha256 TEXT,
    uploaded_by TEXT,
    upload_time TEXT)
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS audit_logs(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        action TEXT,
        timestamp TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS verification_logs(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        evidence_id INTEGER,
        verified_by TEXT,
        verification_time TEXT,
        status TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS tamper_alerts(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        evidence_id INTEGER,
        evidence_title TEXT,
        detected_by TEXT,
        detection_time TEXT,
        original_hash TEXT,
        current_hash TEXT,
        severity TEXT,
        status TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS cases(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        case_id TEXT UNIQUE,
        case_name TEXT,
        description TEXT,
        investigator TEXT,
        priority TEXT,
        status TEXT,
        created_at TEXT
    )
    """)

    conn.commit()
    conn.close()