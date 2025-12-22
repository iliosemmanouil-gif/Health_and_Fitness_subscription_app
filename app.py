from flask import Flask, request, jsonify, send_from_directory
import json, os
from datetime import datetime, timedelta

app = Flask(__name__, static_folder="static")

DATA_FILE = "pelatais.json"

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
          "id": len(pelates) + 1,
          "name": name,
          "months": months,
          "startDate": start_date.strftime("%d/%m/%Y"),
          "endDate": end_date.strftime("%d/%m/%Y"),
          "status": "pending"   
    }

    pelates = load_data()
    pelates.append(pelatis)
    save_data(pelates)

    return jsonify({"message": "Ο πελάτης προστέθηκε!", "pelatis": pelatis})

@app.route("/api/pelatais", methods=["GET"])
def get_pelatais():
    pelates = load_data()
    pending = [p for p in pelates if p.get("status") == "pending"]
    return jsonify(pending)


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

@app.route("/api/approve/<int:pid>", methods=["POST"])
def approve_pelatis(pid):
    pelates = load_data()

    for p in pelates:
        if p.get("id") == pid:
            p["status"] = "approved"

    save_data(pelates)
    return jsonify({"message": "Ο πελάτης εγκρίθηκε"})


@app.route("/api/reject/<int:pid>", methods=["POST"])
def reject_pelatis(pid):
    pelates = load_data()

    for p in pelates:
        if p.get("id") == pid:
            p["status"] = "rejected"

    save_data(pelates)
    return jsonify({"message": "Ο πελάτης απορρίφθηκε"})

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
