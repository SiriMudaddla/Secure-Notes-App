# features/sync_client.py
import json
import requests

def upload_payload(server_url, payload):
    r = requests.post(f"{server_url}/upload", json=payload, timeout=20)
    r.raise_for_status()
    return r.json()

def download_all(server_url):
    r = requests.get(f"{server_url}/download", timeout=20)
    r.raise_for_status()
    return r.json()

def push_encrypted_notes(server_url, notes, versions):
    payload = {"notes": notes, "versions": versions}
    return upload_payload(server_url, payload)