import os
import psycopg2
import psycopg2.extras
from datetime import datetime

DATABASE_URL = os.environ.get("DATABASE_URL")


def get_conn():
    return psycopg2.connect(DATABASE_URL)


def init_db():
    con = get_conn()
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id     BIGINT PRIMARY KEY,
            username    TEXT,
            first_name  TEXT,
            ip          TEXT,
            accepted    BOOLEAN DEFAULT FALSE,
            accepted_at TIMESTAMP,
            invite_link TEXT,
            banned      BOOLEAN DEFAULT FALSE
        )
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_ip ON users(ip)")
    con.commit()
    cur.close()
    con.close()


def ip_already_used(ip: str) -> bool:
    con = get_conn()
    cur = con.cursor()
    cur.execute(
        "SELECT user_id FROM users WHERE ip = %s AND accepted = TRUE AND banned = FALSE",
        (ip,)
    )
    row = cur.fetchone()
    cur.close()
    con.close()
    return row is not None


def user_accepted(user_id: int) -> bool:
    con = get_conn()
    cur = con.cursor()
    cur.execute(
        "SELECT accepted, banned FROM users WHERE user_id = %s",
        (user_id,)
    )
    row = cur.fetchone()
    cur.close()
    con.close()
    if not row:
        return False
    accepted, banned = row
    return bool(accepted) and not bool(banned)


def save_user(user_id: int, username: str, first_name: str, ip: str, invite_link: str):
    con = get_conn()
    cur = con.cursor()
    cur.execute("""
        INSERT INTO users (user_id, username, first_name, ip, accepted, accepted_at, invite_link, banned)
        VALUES (%s, %s, %s, %s, TRUE, %s, %s, FALSE)
        ON CONFLICT (user_id) DO UPDATE SET
            username    = EXCLUDED.username,
            first_name  = EXCLUDED.first_name,
            ip          = EXCLUDED.ip,
            accepted    = TRUE,
            accepted_at = EXCLUDED.accepted_at,
            invite_link = EXCLUDED.invite_link
    """, (user_id, username, first_name, ip, datetime.utcnow(), invite_link))
    con.commit()
    cur.close()
    con.close()


def ban_user(user_id: int):
    con = get_conn()
    cur = con.cursor()
    cur.execute("UPDATE users SET banned = TRUE WHERE user_id = %s", (user_id,))
    con.commit()
    cur.close()
    con.close()


def unban_user(user_id: int):
    con = get_conn()
    cur = con.cursor()
    cur.execute("UPDATE users SET banned = FALSE, accepted = FALSE WHERE user_id = %s", (user_id,))
    con.commit()
    cur.close()
    con.close()


def list_users(limit: int = 10):
    con = get_conn()
    cur = con.cursor()
    cur.execute("""
        SELECT user_id, username, first_name, ip, accepted_at, banned
        FROM users ORDER BY accepted_at DESC NULLS LAST LIMIT %s
    """, (limit,))
    rows = cur.fetchall()
    cur.close()
    con.close()
    return rows
