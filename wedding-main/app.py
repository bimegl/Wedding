import sqlite3
import csv
import io
from functools import wraps
from datetime import datetime
from flask_mail import Mail
import os
from flask import (
    Flask, render_template, request,
    redirect, url_for, session,
    Response
)

import config

from flask_mail import Message
from threading import Thread


app = Flask(__name__)
app.config.from_object(config)


# -------------------
# Database
# -------------------

if os.environ.get("RAILWAY_ENV"):  # Railway sets this automatically
    os.makedirs("/data", exist_ok=True)
    DATABASE_PATH = "/data/app.db"
else:
    os.makedirs("data", exist_ok=True)
    DATABASE_PATH = "data/app.db"


app.config["DATABASE"] = DATABASE_PATH
print("Database path:", os.path.abspath(app.config["DATABASE"]))


# -------------------
# MAIL
# -------------------
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = "trackshare.inbox@gmail.com"
app.config["MAIL_PASSWORD"] = "zmaa yvhd fvwg ezkn"
app.config["MAIL_DEFAULT_SENDER"] = "trackshare.inbox@gmail.com"

mail = Mail(app)
FIXED_EMAIL = "francesca.altavilla2425@gmail.com"








def send_async_email(msg):
    with app.app_context():
        mail.send(msg)


def send_rsvp_email(
    testo,
    participant_email,
    participant_name,
    attending,
    guests,
    bambini,
    accompagnatori,
    notes
):
    try:

        #template_file = "email_yes.html" if attending.lower() == "yes" else "email_no.html"

        template_file = "email.html"
        html_body = render_template(
            template_file,
            testo = testo,
            participant_name=participant_name,
            participant_email=participant_email,
            guests=guests,
            bambini=bambini,
            accompagnatori=accompagnatori,
            notes=notes
        )

        subject = (
            "Conferma RSVP - Lucio e Beatrice"
            if attending.lower() == "yes"
            else "RSVP Ricevuto - Lucio e Beatrice"
        )

        msg = Message(
            subject=subject,
            recipients=[participant_email, FIXED_EMAIL],
            html=html_body
        )

        Thread(target=send_async_email, args=(msg,)).start()

        return True

    except Exception as e:
        print(e)
        return False



def get_db():
    conn = sqlite3.connect(app.config["DATABASE"])
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    db = get_db()
    db.execute("""
        CREATE TABLE IF NOT EXISTS rsvp (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            surname TEXT,
            email TEXT UNIQUE,
            attending TEXT NOT NULL,
            accompagnatori TEXT,
            bambini INTEGER,
            guests INTEGER,
            notes TEXT,
            created_at TEXT NOT NULL
        )
    """)
    db.commit()
    db.close()



# -------------------
# Auth
# -------------------

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("admin"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


# -------------------
# Routes
# -------------------

@app.route("/")
def index():
    return render_template("index.html")


def safe_int(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        return 0

@app.route("/rsvp", methods=["POST"])
def rsvp():
    name = request.form["name"]
    surname = request.form["surname"]
    email = request.form["email"]
    accompagnatori = request.form.get("accompagnatori", "")
    attending = request.form["attending"]
    notes = request.form.get("notes", "")

    # Safely convert numbers
    guests = safe_int(request.form.get("guests", 0))
    numero_bambini = safe_int(request.form.get("bambini", 0))

    db = get_db()

    # Check if email already exists
    existing = db.execute("SELECT * FROM rsvp WHERE email = ?", (email,)).fetchone()
    if existing:
        db.close()
        return render_template("already_rsvp.html", email=email)

    db.execute("""
        INSERT INTO rsvp (name, surname, email, attending, accompagnatori, bambini, guests, notes, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (name, surname, email, attending, accompagnatori, numero_bambini, guests, notes, datetime.now()))

    db.commit()
    db.close()

    full_name = f"{name} {surname}"
   
    if attending == "yes":
        testo = '''
LA TUA PRESENZA È STATA CONFERMATA CON SUCCESSO.<br><br>
NON VEDIAMO L'ORA DI FESTEGGIARE INSIEME A TE.
        '''
    else:
        testo = '''
         ABBIAMO RICEVUTO LA TUA RISPOSTA<br><br>
 CI DISPIACE CHE  <br>
 NON POTRAI ESSERE PRESENTE. <br><br>
GRAZIE DI CUORE PER AVERCI RISPOSTO.
        '''
    
    send_rsvp_email(testo, email, full_name, attending, guests, numero_bambini, accompagnatori, notes)

    return render_template("rsvp.html",
            partecipant_test = testo,
            participant_name=full_name,
            participant_email=email,
            guests=guests,
            bambini=numero_bambini,
            accompagnatori=accompagnatori,
            notes=notes)



# -------------------
# Admin login
# -------------------

@app.route("/login", methods=["GET", "POST"])
def login():

    # already logged in → go directly to admin
    if session.get("admin"):
        return redirect(url_for("admin"))

    if request.method == "POST":

        if (
            request.form["username"] == app.config["ADMIN_USERNAME"]
            and request.form["password"] == app.config["ADMIN_PASSWORD"]
        ):
            session["admin"] = True
            return redirect(url_for("admin"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# -------------------
# Admin panel
# -------------------

@app.route("/admin")
@login_required
def admin():

    db = get_db()
    guests = db.execute(
        "SELECT * FROM rsvp ORDER BY created_at DESC"
    ).fetchall()
    db.close()

    return render_template("admin.html", guests=guests)


# -------------------
# CSV export (Excel friendly)
# -------------------

@app.route("/export")
@login_required
def export():

    db = get_db()
    guests = db.execute("""
        SELECT
            name,
            surname,
            email,
            attending,
            accompagnatori,
            bambini,
            guests,
            notes,
            created_at
        FROM rsvp
        ORDER BY created_at DESC
    """).fetchall()
    db.close()

    output = io.StringIO()

    # Use ; separator → better for European Excel
    writer = csv.writer(
        output,
        delimiter=";",
        quotechar='"',
        quoting=csv.QUOTE_MINIMAL
    )

    # Header row
    writer.writerow([
        "Name",
        "Surname",
        "Email",
        "Attending",
        "Accompagnatori",
        "Bambini",
        "Guests",
        "Notes",
        "Created at"
    ])

    # Data rows
    for r in guests:
        writer.writerow([
            r["name"],
            r["surname"],
            r["email"],
            r["attending"],
            r["accompagnatori"],
            r["bambini"],
            r["guests"],
            r["notes"],
            r["created_at"]
        ])

    # Add UTF-8 BOM so Excel opens correctly
    csv_data = output.getvalue()
    bom = "\ufeff"

    return Response(
        bom + csv_data,
        mimetype="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": "attachment; filename=rsvp.csv"
        }
    )


# Test data
test_data = {
    "participant_name": "Mario Rossi",
    "participant_email": "mario@example.com",
    "guests": 2,
    "bambini": 1,
    "accompagnatori": "Luigi Bianchi; Anna Verdi",
    "notes": "Nessuna allergia"
}

# Endpoint to preview the "attending" email template
@app.route("/test-email/y")
def test_attending_email():
    return render_template("email_yes.html", **test_data)

# Endpoint to preview the "not attending" email template
@app.route("/test-email/n")
def test_not_attending_email():
    return render_template("email_no.html", **test_data)


# -------------------

init_db()

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
