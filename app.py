from flask import Flask, request, jsonify, send_from_directory
import json, os
from datetime import datetime, timedelta
import smtplib
from email.message import EmailMessage


app = Flask(__name__, static_folder="static")

DATA_FILE = "pelatais.json"


# ----------- Ρυθμίσεις Email -----------
EMAIL_SENDER = os.environ.get("ilios.emmanouil@gmail.com")
EMAIL_PASSWORD = os.environ.get("khge ykcq dsau nuuz")
EMAIL_RECEIVER = os.environ.get("hlios.vh@gmail.com")

# ---------------- Βοηθητικές Συναρτήσεις ----------------
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def send_email(pelatis):
    msg = EmailMessage()
    msg["Subject"] = "Νέα Εγγραφή Πελάτη Γυμναστηρίου"
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER

    msg.set_content(
        f"Νέα εγγραφή πελάτη:\n\n"
        f"Ονοματεπώνυμο: {pelatis['name']}\n"
        f"Ημερομηνία Έναρξης: {pelatis['startDate']}\n"
        f"Ημερομηνία Λήξης: {pelatis['endDate']}\n"
    )

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
            smtp.send_message(msg)
    except Exception as e:
        print("Σφάλμα αποστολής email:", e)


# ---------------- API Endpoints ----------------

@app.route("/api/add_pelatis", methods=["POST"])
def add_pelatis():
    data = request.json
    name = data.get("name")
    try:
        months = int(data.get("months", 1))
    except ValueError:
        return jsonify({"message": "Οι μήνες πρέπει να είναι αριθμός!"}), 400

    if not name:
        return jsonify({"message": "Το όνομα είναι υποχρεωτικό!"}), 400

    start_date = datetime.now()
    end_date = start_date + timedelta(days=30 * months)

    pelatis = {
        "name": name,
        "startDate": start_date.strftime("%d/%m/%Y"),
        "endDate": end_date.strftime("%d/%m/%Y")
    }

    pelates = load_data()
    pelates.append(pelatis)
    save_data(pelates)
    send_email(pelatis)

    return jsonify({"message": "Ο πελάτης προστέθηκε!", "pelatis": pelatis})

@app.route("/api/pelatais", methods=["GET"])
def get_pelatais():
    return jsonify(load_data())

@app.route("/api/pelatis/<string:name>", methods=["PUT"])
def update_pelatis(name):
    data = request.json
    pelates = load_data()

    for p in pelates:
        if p.get("name") == name:
            p["name"] = data.get("name", p["name"])
            p["endDate"] = data.get("endDate", p["endDate"])
            save_data(pelates)
            return jsonify({"message": "Ο πελάτης ενημερώθηκε!", "pelatis": p})

    return jsonify({"message": "Δεν βρέθηκε πελάτης!"}), 404

@app.route("/api/pelatis/<string:name>", methods=["DELETE"])
def delete_pelatis(name):
    pelates = load_data()
    new_list = [p for p in pelates if p.get("name") != name]

    if len(new_list) == len(pelates):
        return jsonify({"message": "Δεν βρέθηκε πελάτης!"}), 404

    save_data(new_list)
    return jsonify({"message": f"Ο πελάτης '{name}' διαγράφηκε!"})

# ---------------- HTML Σελίδες ----------------
@app.route("/")
def index():
    return send_from_directory("static", "listapelaton.html")

@app.route("/egrafi")
def egrafi_page():
    return send_from_directory("static", "egrafi.html")

@app.route("/listapelaton")
def listapelaton_page():
    return send_from_directory("static", "listapelaton.html")

# ---------------- Εκκίνηση για Render ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)


