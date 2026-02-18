import os
import threading
from datetime import datetime, timedelta, timezone
import requests
import json
from flask import Flask, render_template, request, redirect, url_for, session
from dotenv import load_dotenv # Lädt .env Datei
from repository import orders_repo
from repository.customer_repo import get_all_orders
from services import math_service
from config import DevelopmentConfig, ProductionConfig
import db
from repository import product_repo 


app = Flask(__name__)

"""
Festlegen einer Route für die Homepage. Der String in den Klammern
bildet das URL-Muster ab, unter dem der folgende Code ausgeführt
werden soll.
z.B.
* @app.route('/')    -> http://127.0.0.1:5000/
* @app.route('/home') -> http://127.0.0.1:5000/home
"""
db.init_app(app)
 

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)


if os.environ.get('FLASK_ENV') == 'development':
    app.config.from_object(DevelopmentConfig)
else:
    app.config.from_object(ProductionConfig)

# Mailgun configuration (HTTP API)

MAILGUN_DOMAIN = os.environ.get('MAILGUN_DOMAIN', '').strip()
MAILGUN_API_KEY = os.environ.get('MAILGUN_API_KEY', '').strip()
MAILGUN_FROM = os.environ.get('MAILGUN_FROM', '').strip()

if not MAILGUN_DOMAIN or not MAILGUN_API_KEY:
    app.logger.warning('Mailgun is not configured. Set MAILGUN_DOMAIN and MAILGUN_API_KEY in Render Environment Variables.')
else:
    app.logger.info('MAILGUN_API_KEY is set (length=%s).', len(MAILGUN_API_KEY))
    app.logger.info('MAILGUN_DOMAIN=%s', MAILGUN_DOMAIN)
    app.logger.info('MAILGUN_FROM=%s', MAILGUN_FROM)

def send_email_via_mailgun(subject, recipients, text):
    if not MAILGUN_DOMAIN or not MAILGUN_API_KEY or not MAILGUN_FROM:
        app.logger.error('Mailgun config missing. Set MAILGUN_DOMAIN, MAILGUN_API_KEY, and MAILGUN_FROM.')
        return False

    if not recipients:
        app.logger.error('No recipients provided for Mailgun send.')
        return False

    app.logger.info(f"Sending email via Mailgun...")
    app.logger.info(f"  From: {MAILGUN_FROM}")
    app.logger.info(f"  To: {recipients}")
    app.logger.info(f"  Subject: {subject}")
    app.logger.info(f"  Domain: {MAILGUN_DOMAIN}")

    url = f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages"
    
    try:
        response = requests.post(
            url,
            auth=("api", MAILGUN_API_KEY),
            data={
                "from": MAILGUN_FROM,
                "to": ",".join(recipients),
                "subject": subject or "",
                "text": text or "",
            },
            timeout=10,
        )
        
        app.logger.info(f"Mailgun response status: {response.status_code}")
        app.logger.info(f"Mailgun response body: {response.text}")
        
        if response.status_code not in (200, 202):
            app.logger.error("Mailgun error %s: %s", response.status_code, response.text)
            return False
        
        app.logger.info("Email sent successfully via Mailgun!")
        return True
        
    except Exception as e:
        app.logger.error(f"Exception during Mailgun request: {str(e)}")
        return False

# Benutzerdaten-Management
def load_users():
    """Lade alle Benutzer aus der users.json Datei"""
    users_file = os.path.join(os.path.dirname(__file__), 'users.json')
    default_users = {
        "admin": "1234",
        "carframe": "poster123"
    }
    
    if os.path.exists(users_file):
        try:
            with open(users_file, 'r') as f:
                return json.load(f)
        except:
            return default_users
    return default_users

def save_users(users):
    """Speichere alle Benutzer in der users.json Datei"""
    users_file = os.path.join(os.path.dirname(__file__), 'users.json')
    try:
        with open(users_file, 'w') as f:
            json.dump(users, f, indent=2)
    except Exception as e:
        app.logger.error(f"Error saving users: {str(e)}")

def send_email_async(subject, recipients, text) -> None:
    def _send():
        try:
            app.logger.info("Email send start (Mailgun)")
            success = send_email_via_mailgun(
                subject=subject or "",
                recipients=recipients or [],
                text=text or "",
            )
            app.logger.info("Email send finished (Mailgun) success=%s", success)
        except Exception as e:
            app.logger.error(
                "Error sending email: %s (%s)",
                str(e),
                type(e).__name__
            )

    threading.Thread(target=_send, daemon=True).start()

@app.context_processor
def cart_context():
    # Anzahl aller Items (berücksichtigt 'quantity') für Anzeige im Navbar-Badge
    cart = session.get('cart_items', [])
    total_count = sum(int(item.get('quantity', 0)) for item in cart)
    return dict(cart_item_count=total_count)

languages = [
    {"name": "Python", "creator": "Guido van Rossum", "year": 1991},
    {"name": "JavaScript", "creator": "Brendan Eich", "year": 1995},
    {"name": "Java", "creator": "James Gosling", "year": 1995},
    {"name": "C#", "creator": "Microsoft", "year": 2000},
    {"name": "Ruby", "creator": "Yukihiro Matsumoto", "year": 1995},
]

cart_items = [
    {"id": 1, "image_url": "static/pictures/2/PorscheGT3RS.png", "name": "Porsche GT3 RS", "size": "A4", "price": 35.95, "quantity": 1},
]

posters = [
    {"id": 1, "name": "F1 Track", "description": "Ein ikonisches Motorsport-Poster, das packende Renn-Action und pure Geschwindigkeit einfängt. Präzise Linienwahl, aerodynamische Effizienz und taktisches Können verschmelzen in der Kurve zu einem intensiven Duell am Limit, ein Statement für echte Racing-Enthusiasten.", "image_base": "F1Track"},
    {"id": 2, "name": "Porsche GT3 RS", "description": "Ein ikonisches Porsche 911 GT3 RS Poster, das kompromisslose Performance und Motorsport-DNA zeigt. Aerodynamische Perfektion, Leichtbau und Rennstrecken-Gene vereinen sich zu purer Fahrleidenschaft, ein Statement für echte Porsche-Enthusiasten.", "image_base": "PorscheGT3RS"},
    {"id": 3, "name": "Ferrari Enzo", "description": "Ein ikonisches Ferrari-Poster, das zeitlose Eleganz und italienische Sportwagen-Tradition verkörpert. Glänzender Lack, ikonisches Emblem und pure Design-Leidenschaft verschmelzen zu einem Symbol automobiler Geschichte, ein Statement für echte Klassiker-Enthusiasten.", "image_base": "FerrariEnzo"},
    {"id": 4, "name": "Jaguar F-Type", "description": "Ein ikonisches Jaguar F-Type Poster, das britische Eleganz und kraftvolle Sportwagen-DNA vereint. Markantes Design, dynamische Linien und beeindruckende Performance verschmelzen zu purer Fahrfaszination, ein Statement für echte Sportwagen-Enthusiasten.", "image_base": "JaguarF-Type"},
    {"id": 5, "name": "Just Drive don't mind", "description": "Ein ikonisches Highway-Poster, das Freiheit, Bewegung und pures Fahrgefühl einfängt. Klare Linien, kräftige Farben und eine starke Frontansicht verschmelzen zu einem modernen Retro-Statement, geschaffen für alle, die einfach fahren und den Moment geniessen.", "image_base": "Highway"},
    {"id": 6, "name": "Ferrari LaFerrari", "description": "Ein ikonisches LaFerrari-Poster, das italienische Ingenieurskunst und kompromisslose Performance vereint. Extreme Leistung, Hybrid-Innovation und zeitloses Design verschmelzen zu purer Supercar-Emotion, ein klares Statement für echte Ferrari-Enthusiasten.", "image_base": "FerrariLaFerrari"},
]

@app.route('/')
def home():
    print(math_service.add(1.0, 2.0))
    app.logger.info("Rendering home page")
    products = product_repo.get_all_products()
    return render_template("home.html", products=products)

@app.route('/result/', defaults={'name': 'Guest'})
@app.route('/result/<name>')
def result(name) -> str:
    app.logger.info(f"Showing result for {name}")
    return render_template("result.html", name=name)

@app.route("/about")
def about() -> str:
    app.logger.info(session.get('test', ''))
    return render_template("about.html", languages=languages)

@app.route("/productpage")
@app.route('/productpage/<id>')
def productpage(id) -> str:
    poster = posters[int(id)-1]
    title = poster["name"]
    description = poster["description"]
    id = poster["id"]
    image_base = poster["image_base"]
    return render_template("ProductPage.html", id=id, title=title, description=description, image_base=image_base)

@app.route("/cashdesk")
def cashdesk() -> str:
    return render_template("cashdesk.html")

@app.route("/login", methods=["GET", "POST"])
def login() -> str:
    # Wenn Formular abgeschickt wurde (POST)
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        
        # Lade Benutzer aus Datei
        users = load_users()
        
        # Überprüfe ob Benutzername existiert und Passwort stimmt
        if username in users and users[username] == password:
            # Login erfolgreich - speichere in Session
            session['logged_in'] = True
            session['username'] = username
            app.logger.info(f"User {username} logged in successfully")
            return redirect(url_for('home'))
        else:
            # Login fehlgeschlagen
            error = "Falscher Benutzername oder Passwort!"
            return render_template("login.html", error=error)
    
    # Bei GET-Request: Zeige Login-Seite
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register() -> str:
    # Wenn Formular abgeschickt wurde (POST)
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()
        
        # Validierung
        if not username:
            error = "Benutzername ist erforderlich!"
            return render_template("register.html", error=error)
        
        if len(username) < 3:
            error = "Benutzername muss mindestens 3 Zeichen lang sein!"
            return render_template("register.html", error=error)
        
        if not password:
            error = "Passwort ist erforderlich!"
            return render_template("register.html", error=error)
        
        if len(password) < 4:
            error = "Passwort muss mindestens 4 Zeichen lang sein!"
            return render_template("register.html", error=error)
        
        if password != confirm_password:
            error = "Passwörter stimmen nicht überein!"
            return render_template("register.html", error=error)
        
        # Lade bestehende Benutzer
        users = load_users()
        
        # Überprüfe ob Benutzername bereits existiert
        if username in users:
            error = "Dieser Benutzername existiert bereits!"
            return render_template("register.html", error=error)
        
        # Neuen Benutzer hinzufügen
        users[username] = password
        save_users(users)
        
        success = "Registrierung erfolgreich! Melde dich jetzt an."
        return render_template("register.html", success=success)
    
    # Bei GET-Request: Zeige Registrierungs-Seite
    return render_template("register.html")

@app.route("/logout")
def logout() -> str:
    # Entferne User aus Session
    session.pop('logged_in', None)
    session.pop('username', None)
    app.logger.info("User logged out")

    return redirect(url_for('home'))

@app.route("/information")
def information() -> str:

    return render_template("information.html")

@app.route("/cart/add/<id>", methods=["POST"])
def add_to_cart(id):
    allowed_ids = {1, 2, 3, 4, 5, 6}
    if int(id) not in allowed_ids:
        return redirect(url_for('index'))


    quantity = max(1, int(request.form.get('quantity', 1)))
    size = request.form.get('size', 'A4')
    frame_option = request.form.get('frame_option')
    cart_items = session.get('cart_items', [])
  
    if size == 'A4':
        unit_price = 35.95
    elif size == 'A3':
        unit_price = 42.95
    else:
        unit_price = 50.95


    if frame_option == 'Ohne Rahmen':
        unit_price -= 10.00

    item_exists = False

    for item in cart_items:
        if (int(item.get('id')) == int(id) and
            item.get('size') == size and
            item.get('frame_option') == frame_option):


            item['quantity'] = int(item.get('quantity', 0)) + quantity

            item['price'] = round(unit_price * item['quantity'], 2)
            item_exists = True
            break


    if not item_exists:
        total_price = round(unit_price * quantity, 2)
        poster_info = posters[int(id)-1]

        cart_items.append({
            'id': int(id),
            'name': poster_info['name'],
            'image_base': poster_info['image_base'],
            'size': size,
            'price': total_price,
            'frame_option': frame_option,
            'quantity': quantity
        })

    session['cart_items'] = cart_items
    session['price'] = sum(item.get('price', 0) for item in cart_items)
    session.modified = True

    return redirect(url_for('productpage', id=id))

@app.route("/cart")
def cart():
    cart_items = session.get('cart_items', [])
    return render_template("cart.html", cart_items=cart_items)


@app.route("/feedback")
def feedback():
    return render_template("feedback.html")

@app.route("/cart/remove/<int:index>", methods=["POST"])
def remove_from_cart(index):
    cart_items = session.get('cart_items', [])
    if 0 <= index < len(cart_items):
        cart_items.pop(index)
        session['cart_items'] = cart_items
        app.logger.info(f"Removed item at index {index}. Remaining items: {cart_items}")
    return '', 204

@app.route("/cart/update/<int:index>", methods=["POST"])
def update_cart_quantity(index):
    cart_items = session.get('cart_items', [])

    if 0 <= index < len(cart_items):
        data = request.get_json()
        quantity = data.get('quantity', 1)

        if quantity > 0:
            item = cart_items[index]

            size = item.get('size', 'A4')
            if size == 'A4':
                unit_price = 35.95
            elif size == 'A3':
                unit_price = 42.95
            else:
                unit_price = 50.95

            if item.get('frame_option') == 'Ohne Rahmen':
                unit_price -= 10.00

            item['quantity'] = quantity

            item['price'] = round(unit_price * quantity, 2)

            session['cart_items'] = cart_items
            session['price'] = sum(item.get('price', 0) for item in cart_items)
            session.modified = True
            app.logger.info(f"Updated item at index {index} to quantity {quantity}")
            return '', 204
    return '', 400

@app.route("/feedbackconfirmation")
def feedbackconfirmation() -> str:
    return render_template("feedbackconfirmation.html")



@app.route("/submit", methods=["POST"])
def submit():
    app.logger.info("Form submitted")
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    message = request.form.get("message", "").strip()

    print(f"Name: {name}")
    print(f"Email: {email}")
    print(f"Nachricht: {message}")

    errors = []
    if sum(c.isalpha() for c in name) < 3:
        errors.append("Name must contain at least 3 letters.")
    if len(message) < 3:
        errors.append("Nachricht must be at least 3 characters.")

    if errors:
        return render_template("about.html", languages=languages, errors=errors,
                               form={"name": name, "email": email, "message": message})

    if not MAILGUN_DOMAIN or not MAILGUN_API_KEY or not MAILGUN_FROM:
        errors.append("Email service not configured.")
        return render_template("about.html", languages=languages, errors=errors,
                               form={"name": name, "email": email, "message": message})

    timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
    send_email_async(
        subject=f"Kontaktformular von {name} | {timestamp}",
        recipients=['nick.noesberger@gmail.com'],
        text=f"Name: {name}\nE-Mail: {email}\nNachricht:\n{message}",
    )

    return redirect(url_for("result", name=name))

@app.route("/checkout", methods=["POST"])
def checkout() -> str:
    app.logger.info(session.get('price'))
    bezahlart = request.form.get("payment_method")
    orders_repo.add_order(
        bestellnummer = str(int(datetime.now().timestamp()) % 100000).zfill(5),
        status = "Bestellt",
        preis = session.get('price', 0.0),
        liefertermin = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'),
        zahlungsart = bezahlart,
        userid = session.get('user_id')
    )
    return render_template("bestellbestaetigung.html")

@app.route("/submit2", methods=["POST"])
def submit2():
    app.logger.info("Form submitted")
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    message = request.form.get("message", "").strip()
    rating = request.form.get("rating", "").strip()

    errors = []

    if sum(c.isalpha() for c in name) < 3:
        errors.append("Name must contain at least 3 letters.")
    if len(message) < 3:
        errors.append("Nachricht must be at least 3 characters.")

    if errors:
        return render_template("about.html", languages=languages, errors=errors,
                               form={"name": name, "email": email, "message": message})

    if not MAILGUN_DOMAIN or not MAILGUN_API_KEY or not MAILGUN_FROM:
        errors.append("Email service not configured.")
        return render_template("about.html", languages=languages, errors=errors,
                               form={"name": name, "email": email, "message": message})

    timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
    send_email_async(
        subject=f"Feedback von {name} | {timestamp}",
        recipients=['nick.noesberger@gmail.com'],
        text=f"Name: {name}\nE-Mail: {email}\nBewertung: {rating}/5\nFeedback:\n{message}",
    )

    return redirect(url_for("feedbackconfirmation", name=name))

@app.route("/add-product", methods=["POST"])
def add_product():
    name = request.form['name']
    price = request.form['price']
    product_repo.add_product(name, price)
    return redirect(url_for("home"))

@app.route("/bestellungen")
def bestellungen() -> str:
    orders = get_all_orders()
    app.logger.info(session.get('test', ''))
    return render_template("bestellungen.html", orders=orders)
    

if __name__ == '__main__':
    app.run(port=5000, debug=True)
