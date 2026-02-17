from db import get_db

def add_product(name, price):
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO products (name, price) VALUES (%s, %s)", (name, price))
        conn.commit()
    except Exception as e:
        conn.rollback()
    finally:
        cur.close()

def get_all_products():
    con = get_db()
    cur = con.cursor()
    cur.execute("SELECT id, name, price FROM products")
    products = cur.fetchall()
    cur.close()
    return products