from db import get_db


def get_all_orders():
    con = get_db()
    cur = con.cursor()
    cur.execute("SELECT * FROM orders")
    orders = cur.fetchall()
    cur.close()
    return orders

def get_orders_by_customer_id(customer_id):
    con = get_db()
    cur = con.cursor()
    cur.execute("SELECT * FROM orders WHERE userid = %s", (customer_id,))
    orders = cur.fetchall()
    cur.close()
    return orders