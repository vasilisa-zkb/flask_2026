import os
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mail import Mail, Message
from dotenv import load_dotenv # Lädt .env Datei
from services import math_service
from config import DevelopmentConfig, ProductionConfig


app = Flask(__name__)

"""
Festlegen einer Route für die Homepage. Der String in den Klammern
bildet das URL-Muster ab, unter dem der folgende Code ausgeführt
werden soll.
z.B.
* @app.route('/')    -> http://127.0.0.1:5000/
* @app.route('/home') -> http://127.0.0.1:5000/home
"""


dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)


if os.environ.get('FLASK_ENV') == 'development':
    app.config.from_object(DevelopmentConfig)
else:
    app.config.from_object(ProductionConfig)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'sekreteriatcarframe@gmail.com'
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', '')
app.config['MAIL_DEFAULT_SENDER'] = 'sekreteriatcarframe@gmail.com'

mail = Mail(app)

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
    {"id": 1, "image_url": "static/posters/w.png", "name": "Porsche GT3 RS", "size": "A4", "price": 38, "quantity": 1},
]

posters = [
    {"id": 1, "name": "F1 Track", "description": "Ein ikonisches Motorsport-Poster, das packende Renn-Action und pure Geschwindigkeit einfängt. Präzise Linienwahl, aerodynamische Effizienz und taktisches Können verschmelzen in der Kurve zu einem intensiven Duell am Limit – ein Statement für echte Racing-Enthusiasten."},
    {"id": 2, "name": "Porsche GT3 RS", "description": "Ein ikonisches Porsche 911 GT3 RS Poster, das kompromisslose Performance und Motorsport-DNA zeigt. Aerodynamische Perfektion, Leichtbau und Rennstrecken-Gene vereinen sich zu purer Fahrleidenschaft – ein Statement für echte Porsche-Enthusiasten."},
    {"id": 3, "name": "Ferrari Enzo", "description": "Ein ikonisches Ferrari-Poster, das zeitlose Eleganz und italienische Sportwagen-Tradition verkörpert. Glänzender Lack, ikonisches Emblem und pure Design-Leidenschaft verschmelzen zu einem Symbol automobiler Geschichte – ein Statement für echte Klassiker-Enthusiasten."},
    {"id": 4, "name": "Jaguar F-Type", "description": "Ein ikonisches Jaguar F-Type Poster, das britische Eleganz und kraftvolle Sportwagen-DNA vereint. Markantes Design, dynamische Linien und beeindruckende Performance verschmelzen zu purer Fahrfaszination – ein Statement für echte Sportwagen-Enthusiasten."},
    {"id": 5, "name": "Just Drive don't mind", "description": "Ein ikonisches Highway-Poster, das Freiheit, Bewegung und pures Fahrgefühl einfängt. Klare Linien, kräftige Farben und eine starke Frontansicht verschmelzen zu einem modernen Retro-Statement – geschaffen für alle, die einfach fahren und den Moment geniessen."},
    {"id": 6, "name": "Ferrari LaFerrari", "description": "Ein ikonisches LaFerrari-Poster, das italienische Ingenieurskunst und kompromisslose Performance vereint. Extreme Leistung, Hybrid-Innovation und zeitloses Design verschmelzen zu purer Supercar-Emotion – ein klares Statement für echte Ferrari-Enthusiasten."},
]

@app.route('/')
def home():
    print(math_service.add(1.0, 2.0))
    app.logger.info("Rendering home page")
    return render_template("home.html")

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
    return render_template("ProductPage.html", id=id, title=title, description=description)

@app.route("/cashdesk")
def cashdesk() -> str:
    return render_template("cashdesk.html")

@app.route("/login")
def login() -> str:
    return render_template("login.html")

@app.route("/information")
def information() -> str:

    return render_template("information.html")

@app.route("/cart/add/<id>", methods=["POST"])
def add_to_cart(id) -> str:
    allowed_ids = {1, 2, 3, 4, 5, 6}
    try:
        product_id = int(id)
    except ValueError:
        app.logger.warning(f"Invalid product id: {id}")
        return redirect(url_for('productpage', id=id))

    if product_id in allowed_ids:
        quantity = int(request.form.get('quantity', 1))
        if quantity < 1:
            quantity = 1
        size = request.form.get('size', 'A4')
        cart_items = session.get('cart_items', [])

        # Wenn Produkt im Warenkorb 
        found = False
        for item in cart_items:
            try:
                existing_id = int(item.get('id', item.get('id')))
            except Exception:
                existing_id = item.get('id')

            if int(existing_id) == product_id and item.get('size') == size:
                item['quantity'] = item.get('quantity', 0) + quantity
                found = True
                break

        if not found:
            cart_items.append({'id': product_id, 'name': posters[product_id-1]['name'], 'size': size, 'price': 38, 'quantity': quantity})

        session['cart_items'] = cart_items
        app.logger.info(f"Added item {product_id} (size {size}) x{quantity} to cart. Current cart items: {cart_items}")
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
            cart_items[index]['quantity'] = quantity
            session['cart_items'] = cart_items
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

    try:
        msg = Message(
            subject=f"Kontaktformular von {name}",
            recipients=['sekreteriatcarframe@gmail.com'],
            body=f"Name: {name}\nE-Mail: {email}\nNachricht:\n{message}"
        )
        mail.send(msg)
        app.logger.info(f"Email sent successfully to sekreteriatcarframe@gmail.com")
    except Exception as e:
        app.logger.error(f"Error sending email: {str(e)}")

    return redirect(url_for("result", name=name))

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

    try:
        msg = Message(
            subject=f"Feedback von {name}",
            recipients=['sekreteriatcarframe@gmail.com'],
            body=f"Name: {name}\nE-Mail: {email}\nBewertung: {rating}/5\nFeedback:\n{message}"
        )
        mail.send(msg)
        app.logger.info(f"Feedback email sent successfully to sekreteriatcarframe@gmail.com")
    except Exception as e:
        app.logger.error(f"Error sending feedback email: {str(e)}")

    return redirect(url_for("feedbackconfirmation", name=name))


if __name__ == '__main__':
    app.run(port=5000)