
import email
from db import get_db


def save_user_login(email, password):
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO users (email, password) VALUES (%s, %s)", (email, password))
        conn.commit()
    except Exception as e:
        conn.rollback()
    finally:
        cur.close()

def get_all_users():
    con = get_db()
    cur = con.cursor()
    cur.execute("SELECT id, email FROM users")
    users = cur.fetchall()
    cur.close()
    return users

def get_user_by_email(email):
        con = get_db()
        cur = con.cursor()
        cur.execute("SELECT id, email, password FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()
        return user