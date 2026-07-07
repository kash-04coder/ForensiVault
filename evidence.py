import hashlib
import sqlite3
import os
from datetime import datetime
from encryption import encrypt_file
from audit import log_action

UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def calculate_hash(file_path):

    sha256 = hashlib.sha256()

    with open(file_path,"rb") as f:

        while chunk := f.read(4096):
            sha256.update(chunk)

    return sha256.hexdigest()


def save_evidence(case_id, title, file, username):

    os.makedirs("uploads", exist_ok=True)

    filename = os.path.basename(file.name)

    file_path = os.path.join("uploads", filename)

    print("Saving to:", file_path)

    with open(file_path, "wb") as f:
        f.write(file.getbuffer())

    file_hash = calculate_hash(file_path)
    encrypted_path = encrypt_file(file_path)
    # save to database...

    conn = sqlite3.connect("forensic.db")
    c = conn.cursor()

    c.execute("""
    INSERT INTO evidence(
    case_id,
    title,
    filename,
    filepath,
    encrypted_path,
    sha256,
    uploaded_by,
    upload_time
    )
    VALUES(?,?,?,?,?,?,?,?)
    """,
    (
        case_id,
        title,
        file.name,
        file_path,
        encrypted_path,
        file_hash,
        username,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    c.execute("""
    INSERT INTO custody(
    evidence_id,
    action,
    person,
    timestamp
    )
    VALUES(?,?,?,?)
    """,
    (
        c.lastrowid,
        "Evidence Registered",
        username,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    # os.remove(file_path)


    conn.commit()
    conn.close()

    log_action(
        username,
        f"Encrypted Evidence: {title}"
    )

    return file_hash