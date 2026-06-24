# features/versioning.py
import json
import os
from datetime import datetime

VERSION_FILE = "versions_streamlit.json"

def load_versions():
    if not os.path.exists(VERSION_FILE):
        return {}
    with open(VERSION_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_versions(data):
    with open(VERSION_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def add_version(versions, title, version_obj):
    versions.setdefault(title, []).append(version_obj)
    save_versions(versions)
    return versions

def create_version_record(version_id, nonce, ciphertext):
    return {
        "version_id": version_id,
        "nonce": nonce,
        "ciphertext": ciphertext,
        "ts": datetime.now().isoformat()
    }