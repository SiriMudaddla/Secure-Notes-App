# backend/sync_server.py
from flask import Flask, request, jsonify
import os
import json

app = Flask(__name__)
STORE_DIR = "sync_store"
STORE_FILE = os.path.join(STORE_DIR, "remote_store.json")

os.makedirs(STORE_DIR, exist_ok=True)

def load_store():
    if not os.path.exists(STORE_FILE):
        return {"notes": {}, "versions": {}}
    with open(STORE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_store(data):
    with open(STORE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

@app.route("/upload", methods=["POST"])
def upload():
    incoming = request.get_json(force=True)
    store = load_store()
    store["notes"].update(incoming.get("notes", {}))
    for k, arr in incoming.get("versions", {}).items():
        store["versions"].setdefault(k, []).extend(arr)
    save_store(store)
    return jsonify({"status": "ok"})

@app.route("/download", methods=["GET"])
def download():
    return jsonify(load_store())

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)