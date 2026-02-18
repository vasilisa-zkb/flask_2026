from db import get_db

def add_order(bestellnummer, status, preis, liefertermin, zahlungsart, userid):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO orders (bestellnummer, status, preis, liefertermin, zahlungsart, userid) VALUES (%s, %s, %s, %s, %s, %s)",
        (bestellnummer, status, preis, liefertermin, zahlungsart, userid)
    )
    db.commit()