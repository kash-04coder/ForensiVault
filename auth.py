import sqlite3
import bcrypt

def create_default_admin():
    conn = sqlite3.connect("forensic.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username='admin'")
    user = c.fetchone()
    if not user:
        password = bcrypt.hashpw(
            "admin123".encode(),
            bcrypt.gensalt()
        )
        c.execute(
            "INSERT INTO users(username,password,role) VALUES(?,?,?)",
            ("admin", password.decode(), "Admin")
        )
        conn.commit()
    conn.close()


def login(username,password):
    conn = sqlite3.connect("forensic.db")
    c = conn.cursor()
    c.execute(
        "SELECT password,role FROM users WHERE username=?",
        (username,)
    )
    result = c.fetchone()
    conn.close()
    if result:
        stored_password, role = result
        if bcrypt.checkpw(
            password.encode(),
            stored_password.encode()
        ):
            return role
    return None


def create_user(username, password, role):
    conn = sqlite3.connect("forensic.db")
    c = conn.cursor()
    hashed_password = bcrypt.hashpw(
        password.encode(),
        bcrypt.gensalt()
    )
    try:
        c.execute(
            """
            INSERT INTO users(
            username,
            password,
            role
            )
            VALUES(?,?,?)
            """,
            (
                username,
                hashed_password.decode(),
                role
            )
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def delete_user(user_id):
    conn = sqlite3.connect("forensic.db")
    c = conn.cursor()
    c.execute(
        "DELETE FROM users WHERE id=?",
        (user_id,)
    )
    conn.commit()
    conn.close()

def get_users():
    conn = sqlite3.connect("forensic.db")
    users = conn.execute("""
        SELECT id, username, role
        FROM users
        ORDER BY username
    """).fetchall()
    conn.close()
    return users

def delete_user(user_id):
    conn = sqlite3.connect("forensic.db")
    conn.execute(
        "DELETE FROM users WHERE id=?",
        (user_id,)
    )
    conn.commit()
    conn.close()

def update_role(user_id, role):
    conn = sqlite3.connect("forensic.db")
    conn.execute(
        "UPDATE users SET role=? WHERE id=?",
        (role, user_id)
    )
    conn.commit()
    conn.close()