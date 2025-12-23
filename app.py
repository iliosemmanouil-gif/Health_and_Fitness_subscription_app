from flask import Flask, request, jsonify, send_from_directory
import json, os
from datetime import datetime, timedelta

app = Flask(__name__, static_folder="static")
DATA_FILE = "pelatais.json"

# ---------------- Helpers ----------------
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ---------------- ΕΓΓΡΑΦΗ (PENDING) ----------------
@app.route("/api/add_pelatis", methods=["POST"])
def add_pelatis():
    data = request.json
    name = data.get("name")
    months = int(data.get("months", 1))

    if not name:
        return jsonify({"message": "Το όνομα είναι υποχρεωτικό"}), 400

    pelates = load_data()

    pelatis = {
        "name": name,
        "months": months,
        "startDate": "",
        "endDate": "",
        "status": "pending"
    }

    pelates.append(pelatis)
    save_data(pelates)

    return jsonify({"message": "Η αίτηση καταχωρήθηκε και περιμένει έγκριση"})

# ---------------- ΛΙΣΤΑ ----------------
@app.route("/api/pelatais", methods=["GET"])
def get_pelatais():
    return jsonify(load_data())

# ---------------- ΑΠΟΔΟΧΗ ----------------
@app.route("/api/approve/<string:name>", methods=["POST"])
def approve(name):
    pelates = load_data()

    for p in pelates:
        if p["name"] == name and p["status"] == "pending":
            start = datetime.now()
            end = start + timedelta(days=30 * p["months"])
            p["startDate"] = start.strftime("%d/%m/%Y")
            p["endDate"] = end.strftime("%d/%m/%Y")
            p["status"] = "approved"

    save_data(pelates)
    return jsonify({"message": "Εγκρίθηκε"})

# ---------------- ΑΠΟΡΡΙΨΗ ----------------
@app.route("/api/reject/<string:name>", methods=["POST"])
def reject(name):
    pelates = load_data()
    pelates = [p for p in pelates if p["name"] != name]
    save_data(pelates)
    return jsonify({"message": "Απορρίφθηκε"})

# ---------------- ΚΑΡΤΑ ----------------
@app.route("/card/<string:name>")
def card(name):
    pelates = load_data()
    for p in pelates:
        if p["name"] == name and p["status"] == "approved":
            return f"""
            <h2>Ψηφιακή Κάρτα</h2>
            <p>Όνομα: {p['name']}</p>
            <p>Έναρξη: {p['startDate']}</p>
            <p>Λήξη: {p['endDate']}</p>
            """
    return "Δεν υπάρχει ενεργή συνδρομή"

# ---------------- ΣΕΛΙΔΕΣ ----------------
@app.route("/")
def index():
    return send_from_directory("static", "listapelaton.html")

@app.route("/egrafi")
def egrafi():
    return send_from_directory("static", "egrafi.html")

@app.route("/listapelaton")
def listapelaton():
    return send_from_directory("static", "listapelaton.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)




