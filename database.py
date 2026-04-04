import sqlite3
from datetime import datetime

DB_PATH = "moderador.db"

def init_db():
    con = sqlite3.connect(DB_PATH)
    con.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id     INTEGER PRIMARY KEY,
            username    TEXT,
            first_name  TEXT,
            ip          TEXT,
            accepted    INTEGER DEFAULT 0,
            accepted_at TEXT,
            invite_link TEXT,
            banned      INTEGER DEFAULT 0
        )
    """)
    # migração: adiciona coluna banned se não existir
    try:
        con.execute("ALTER TABLE users ADD COLUMN banned INTEGER DEFAULT 0")
    except Exception:
        pass
    con.execute("CREATE INDEX IF NOT EXISTS idx_ip ON users(ip)")
    con.commit()
    con.close()

def ip_already_used(ip: str) -> bool:
    con = sqlite3.connect(DB_PATH)
    row = con.execute(
        "SELECT user_id FROM users WHERE ip = ? AND accepted = 1 AND banned = 0", (ip,)
    ).fetchone()
    con.close()
    return row is not None

def user_accepted(user_id: int) -> bool:
    con = sqlite3.connect(DB_PATH)
    row = con.execute(
        "SELECT accepted, banned FROM users WHERE user_id = ?", (user_id,)
    ).fetchone()
    con.close()
    if not row:
        return False
    accepted, banned = row
    return bool(accepted) and not bool(banned)

def save_user(user_id: int, username: str, first_name: str, ip: str, invite_link: str):
    con = sqlite3.connect(DB_PATH)
    con.execute("""
        INSERT INTO users (user_id, username, first_name, ip, accepted, accepted_at, invite_link, banned)
        VALUES (?, ?, ?, ?, 1, ?, ?, 0)
        ON CONFLICT(user_id) DO UPDATE SET
            username    = excluded.username,
            first_name  = excluded.first_name,
            ip          = excluded.ip,
            accepted    = 1,
            accepted_at = excluded.accepted_at,
            invite_link = excluded.invite_link
    """, (user_id, username, first_name, ip, datetime.utcnow().isoformat(), invite_link))
    con.commit()
    con.close()

def ban_user(user_id: int):
    con = sqlite3.connect(DB_PATH)
    con.execute("UPDATE users SET banned = 1 WHERE user_id = ?", (user_id,))
    con.commit()
    con.close()

def unban_user(user_id: int):
    con = sqlite3.connect(DB_PATH)
    con.execute("UPDATE users SET banned = 0, accepted = 0 WHERE user_id = ?", (user_id,))
    con.commit()
    con.close()

def list_users(limit: int = 10):
    con = sqlite3.connect(DB_PATH)
    rows = con.execute("""
        SELECT user_id, username, first_name, ip, accepted_at, banned
        FROM users ORDER BY accepted_at DESC LIMIT ?
    """, (limit,)).fetchall()
    con.close()
    return rows
