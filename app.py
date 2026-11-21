
from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import json

app = Flask(__name__)

# =========================
# ADMIN LOGIN SETTINGS
# =========================

app.secret_key = "pathshala-tournament-admin-secret"

ADMIN_USERNAME = "pathshala"
ADMIN_PASSWORD = "pathshala@001"


# =========================
# DATABASE
# =========================

def create_database():

    conn = sqlite3.connect("tournament.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS football_registrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            registration_data TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# Create database when app starts
create_database()


# =========================
# HOME PAGE
# =========================

@app.route("/")
def home():
    return render_template("index.html")


# =========================
# FOOTBALL REGISTRATION
# =========================

@app.route("/football", methods=["GET", "POST"])
def football():

    if request.method == "POST":

        data = request.form.to_dict()

        conn = sqlite3.connect("tournament.db")
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO football_registrations (registration_data)
            VALUES (?)
        """, (json.dumps(data),))

        conn.commit()
        conn.close()

        return render_template(
            "success.html",
            registration_data=data,
            sport="Football"
        )

    return render_template("football.html")


# =========================
# FOOTBALL INFO
# =========================

@app.route("/football-info")
def football_info():
    return render_template("football-info.html")


# =========================
# ADMIN LOGIN
# =========================

@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:

            session["admin_logged_in"] = True

            return redirect(url_for("admin_dashboard"))

        return render_template(
            "admin-login.html",
            error="Invalid username or password."
        )

    return render_template("admin-login.html")


# =========================
# ADMIN DASHBOARD
# =========================

@app.route("/admin-dashboard")
def admin_dashboard():

    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    conn = sqlite3.connect("tournament.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, registration_data
        FROM football_registrations
        ORDER BY id DESC
    """)

    football_rows = cursor.fetchall()
    conn.close()

    football_registrations = []

    for row in football_rows:

        registration_id = row[0]
        data = json.loads(row[1])

        data["registration_id"] = registration_id
        football_registrations.append(data)

    football_count = len(football_registrations)
    total_count = football_count

    return render_template(
        "admin-dashboard.html",
        football_registrations=football_registrations,
        football_count=football_count,
        total_count=total_count
    )


# =========================
# ADMIN LOGOUT
# =========================

@app.route("/admin-logout")
def admin_logout():

    session.pop("admin_logged_in", None)

    return redirect(url_for("admin_login"))


# =========================
# VIEW ALL REGISTRATIONS
# =========================

@app.route("/registrations")
def registrations():

    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    conn = sqlite3.connect("tournament.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT registration_data
        FROM football_registrations
        ORDER BY id DESC
    """)

    football_rows = cursor.fetchall()
    conn.close()

    football_registrations = []

    for row in football_rows:

        data = json.loads(row[0])
        football_registrations.append(data)

    return render_template(
        "registrations.html",
        football_registrations=football_registrations
    )


# =========================
# DELETE REGISTRATION
# =========================

@app.route(
    "/delete-registration/<sport>/<int:registration_id>",
    methods=["POST"]
)
def delete_registration(sport, registration_id):

    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    # Only Football registrations can be deleted
    if sport != "football":
        return redirect(url_for("admin_dashboard"))

    conn = sqlite3.connect("tournament.db")
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM football_registrations WHERE id = ?",
        (registration_id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("admin_dashboard"))


# =========================
# MY REGISTRATION
# =========================

@app.route("/my-registration", methods=["GET", "POST"])
def my_registration():

    registration = None
    sport = None

    if request.method == "POST":

        email = request.form.get("email", "").strip()
        sport = request.form.get("sport", "").strip()

        if sport != "Football":

            return render_template(
                "my-registration.html",
                registration=None,
                sport=None,
                error="Please select Football."
            )

        conn = sqlite3.connect("tournament.db")
        cursor = conn.cursor()

        cursor.execute("""
            SELECT registration_data
            FROM football_registrations
            ORDER BY id DESC
        """)

        rows = cursor.fetchall()
        conn.close()

        for row in rows:

            data = json.loads(row[0])

            if data.get("email", "").strip().lower() == email.lower():

                registration = data
                break

    return render_template(
        "my-registration.html",
        registration=registration,
        sport=sport
    )


# =========================
# ABOUT US
# =========================

@app.route("/about")
def about():
    return render_template("about.html")


# =========================
# OUR JOURNEY
# =========================

@app.route("/our-journey")
def our_journey():
    return render_template("our-journey.html")


# =========================
# ACADEMICS
# =========================

@app.route("/academics")
def academics():
    return render_template("academics.html")


# =========================
# SPORTS
# =========================

@app.route("/sports")
def sports():
    return render_template("sports.html")


# =========================
# CAMPUS
# =========================

@app.route("/campus")
def campus():
    return render_template("campus.html")


# =========================
# CONTACT
# =========================

@app.route("/contact")
def contact():
    return render_template("contact.html")


# =========================
# START WEBSITE
# =========================

if __name__ == "__main__":
    app.run(debug=True)
