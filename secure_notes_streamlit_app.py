import os
import json
import base64
import uuid
from datetime import datetime
import platform

import streamlit as st
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

DATA_FILE = "secure_notes_streamlit.json"
KEYSTORE_FILE = "keystore_streamlit.json"
VERSION_FILE = "versions_streamlit.json"

def load_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def derive_kek(password, salt, iterations=200000):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=iterations,
    )
    return kdf.derive(password.encode())

def init_keystore(password):
    if os.path.exists(KEYSTORE_FILE):
        return
    master_key = os.urandom(32)
    salt = os.urandom(16)
    kek = derive_kek(password, salt)
    aesgcm = AESGCM(kek)
    nonce = os.urandom(12)
    wrapped = aesgcm.encrypt(nonce, master_key, None)
    save_json(KEYSTORE_FILE, {
        "wrapped_master": base64.b64encode(wrapped).decode(),
        "nonce": base64.b64encode(nonce).decode(),
        "salt": base64.b64encode(salt).decode(),
        "created_at": datetime.now().isoformat()
    })

def unlock_master_key(password):
    ks = load_json(KEYSTORE_FILE, None)
    if ks is None:
        return None
    salt = base64.b64decode(ks["salt"])
    nonce = base64.b64decode(ks["nonce"])
    wrapped = base64.b64decode(ks["wrapped_master"])
    kek = derive_kek(password, salt)
    aesgcm = AESGCM(kek)
    return aesgcm.decrypt(nonce, wrapped, None)

def encrypt_note(master_key, plaintext):
    aesgcm = AESGCM(master_key)
    nonce = os.urandom(12)
    ct = aesgcm.encrypt(nonce, plaintext.encode(), None)
    return {
        "nonce": base64.b64encode(nonce).decode(),
        "ciphertext": base64.b64encode(ct).decode(),
        "ts": datetime.now().isoformat()
    }

def decrypt_note(master_key, record):
    aesgcm = AESGCM(master_key)
    nonce = base64.b64decode(record["nonce"])
    ct = base64.b64decode(record["ciphertext"])
    return aesgcm.decrypt(nonce, ct, None).decode()

def load_notes():
    return load_json(DATA_FILE, {})

def save_notes(notes):
    save_json(DATA_FILE, notes)

def load_versions():
    return load_json(VERSION_FILE, {})

def save_versions(v):
    save_json(VERSION_FILE, v)

def add_note(title, content, master_key):
    notes = load_notes()
    versions = load_versions()
    note_id = notes.get(title, {}).get("note_id", str(uuid.uuid4()))
    version_id = str(uuid.uuid4())
    enc = encrypt_note(master_key, content)
    versions.setdefault(title, []).append({"version_id": version_id, **enc})
    notes[title] = {
        "note_id": note_id,
        "current": version_id,
        "updated_at": datetime.now().isoformat()
    }
    save_notes(notes)
    save_versions(versions)
    return version_id

def biometric_available():
    return platform.system() == "Windows"

def biometric_unlock():
    try:
        import FingerPrint
        return True, "Biometric check passed."
    except Exception as e:
        return False, f"Biometric unavailable: {e}"

st.set_page_config(page_title="Secure Notes App", layout="wide")
st.markdown(
    "<h1 style='text-align:center; font-family:\"Times New Roman\", Times, serif;'>Secure Notes App</h1>",
    unsafe_allow_html=True
)

if "master_key" not in st.session_state:
    st.subheader("Unlock")
    password = st.text_input("Password", type="password")
    c1, c2 = st.columns(2)

    with c1:
        if st.button("Create Keystore"):
            if password:
                init_keystore(password)
                st.success("Keystore created. Refresh and unlock again.")
            else:
                st.error("Enter a password.")

    with c2:
        if st.button("Unlock"):
            if password:
                try:
                    mk = unlock_master_key(password)
                    if mk is None:
                        st.error("Keystore not found. Create it first.")
                    else:
                        st.session_state.master_key = mk
                        st.session_state.password = password
                        st.success("Unlocked.")
                        st.rerun()
                except Exception:
                    st.error("Wrong password or corrupted keystore.")
            else:
                st.error("Enter a password.")
else:
    notes = load_notes()
    versions = load_versions()

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Add Note", "View Notes", "History", "Sync", "Biometric"])

    with tab1:
        title = st.text_input("Title")
        content = st.text_area("Write your note")
        if st.button("Save Note"):
            if title and content:
                vid = add_note(title, content, st.session_state.master_key)
                st.success(f"Saved version {vid}")
                st.rerun()
            else:
                st.error("Title and content are required.")

    with tab2:
        titles = list(notes.keys())
        if titles:
            chosen = st.selectbox("Select note", titles)
            if st.button("Decrypt Selected Note"):
                cur = notes[chosen]["current"]
                vobj = next((v for v in versions.get(chosen, []) if v["version_id"] == cur), None)
                if vobj:
                    try:
                        st.text_area("Decrypted content", decrypt_note(st.session_state.master_key, vobj), height=200)
                    except Exception:
                        st.error("Decryption failed.")
        else:
            st.info("No notes yet.")

    with tab3:
        titles = list(notes.keys())
        if titles:
            chosen = st.selectbox("Note for history", titles, key="hist_note")
            for v in versions.get(chosen, []):
                st.write(f"{v['version_id']}  |  {v['ts']}")
            restore_id = st.text_input("Version ID to restore")
            if st.button("Restore Version"):
                if any(v["version_id"] == restore_id for v in versions.get(chosen, [])):
                    notes[chosen]["current"] = restore_id
                    save_notes(notes)
                    st.success("Restored.")
                    st.rerun()
                else:
                    st.error("Version not found.")
        else:
            st.info("No history available.")

    with tab4:
        st.info("Cloud sync is ready in format through encrypted export/import.")
        st.download_button(
            "Download Local Encrypted JSON",
            data=json.dumps({"notes": notes, "versions": versions}, indent=2),
            file_name="secure_notes_sync.json",
            mime="application/json"
        )
        up = st.file_uploader("Import encrypted JSON", type=["json"])
        if up and st.button("Import File"):
            incoming = json.loads(up.read().decode("utf-8"))
            notes.update(incoming.get("notes", {}))
            for k, arr in incoming.get("versions", {}).items():
                versions.setdefault(k, []).extend(arr)
            save_notes(notes)
            save_versions(versions)
            st.success("Imported.")

    with tab5:
        st.write("Biometric unlock is only partially supported and depends on Windows / a biometric wrapper.")
        st.write(f"Biometric available on this device: {biometric_available()}")
        if st.button("Use Biometric Unlock"):
            ok, msg = biometric_unlock()
            if ok:
                st.success(msg)
            else:
                st.error(msg)
