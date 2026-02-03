import os
from flask import Flask, render_template, request, redirect, url_for
from dotenv import load_dotenv # Lädt .env Datei
from services import math_service
from config import DevelopmentConfig, ProductionConfig

# Definieren einer Variable, die die aktuelle Datei zum Zentrum
# der Anwendung macht.
app = Flask(__name__)

"""
Festlegen einer Route für die Homepage. Der String in den Klammern
bildet das URL-Muster ab, unter dem der folgende Code ausgeführt
werden soll.
z.B.
* @app.route('/')    -> http://127.0.0.1:5000/
* @app.route('/home') -> http://127.0.0.1:5000/home
"""

#-------------------------------
#Vorbereitungen
# 1. .env laden (macht lokal Variablen verfügbar, auf Render passiert nichts)
load_dotenv()


# 2. Config wählen
if os.environ.get('FLASK_ENV') == 'development':
    app.config.from_object(DevelopmentConfig)
else:
    app.config.from_object(ProductionConfig)
#-------------------------------

# mock data
languages = [
    {"name": "Python", "creator": "Guido van Rossum", "year": 1991},
    {"name": "JavaScript", "creator": "Brendan Eich", "year": 1995},
    {"name": "Java", "creator": "James Gosling", "year": 1995},
    {"name": "C#", "creator": "Microsoft", "year": 2000},
    {"name": "Ruby", "creator": "Yukihiro Matsumoto", "year": 1995},
]

cart_items = [
    {"id": 1, "image_url": "static\posters\w.png", "name": "Porsche GT3 RS", "size": "A4", "price": 38, "quantity": 1},

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
    return render_template("about.html", languages=languages)

@app.route("/cashdesk")
def cashdesk() -> str:
    return render_template("cashdesk.html")

@app.route("/information")
def information() -> str:
    return render_template("information.html")

@app.route("/cart")
def cart():
    return render_template("cart.html", cart_items=cart_items)


@app.route("/feedback")
def feedback():
    return render_template("feedback.html")


@app.route("/submit", methods=["POST"])
def submit():
    app.logger.info("Form submitted")
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    message = request.form.get("message", "").strip()

    errors = []
    # count letters only
    if sum(c.isalpha() for c in name) < 3:
        errors.append("Name must contain at least 3 letters.")
    if len(message) < 10:
        errors.append("Nachricht must be at least 10 characters.")

    if errors:
        # re-render about page with errors and previous form values
        return render_template("about.html", languages=languages, errors=errors,
                               form={"name": name, "email": email, "message": message})

    return redirect(url_for("result", name=name))



if __name__ == '__main__':
    app.run(port=5000)