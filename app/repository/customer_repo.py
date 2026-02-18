from db import get_db


def get_all_orders():
    con = get_db()
    cur = con.cursor()
    cur.execute("SELECT * FROM orders")
    orders = cur.fetchall()
    cur.close()
    return orders