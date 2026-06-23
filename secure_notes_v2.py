# secure_notes_v2.py
import os, json, base64, uuid
from datetime import datetime
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

CONFIG_FILE = "keystore.json"
DATA_FILE = "secure_notes_v2.json"

def pbkdf2_derive(password: str, salt: bytes, iterations=200000):
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=iterations)
    return kdf.derive(password.encode())

def new_master_key():
    return os.urandom(32)

def wrap_master(master_key: bytes, password: str):
    salt = os.urandom(16)
    kek = pbkdf2_derive(password, salt)
    aesgcm = AESGCM(kek)
    nonce = os.urandom(12)
    wrapped = aesgcm.encrypt(nonce, master_key, None)
    return {'wrapped': base64.b64encode(wrapped).decode(), 'nonce': base64.b64encode(nonce).decode(), 'salt': base64.b64encode(salt).decode(), 'kdf_iters':200000}

def unwrap_master(obj, password: str):
    salt = base64.b64decode(obj['salt'])
    nonce = base64.b64decode(obj['nonce'])
    wrapped = base64.b64decode(obj['wrapped'])
    kek = pbkdf2_derive(password, salt)
    aesgcm = AESGCM(kek)
    return aesgcm.decrypt(nonce, wrapped, None)

def save_config(cfg):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(cfg, f)

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return None
    with open(CONFIG_FILE,'r') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE,'w') as f:
        json.dump(data, f)

def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE,'r') as f:
        return json.load(f)

def encrypt_with_master(master_key: bytes, plaintext: str):
    aesgcm = AESGCM(master_key)
    nonce = os.urandom(12)
    ct = aesgcm.encrypt(nonce, plaintext.encode(), None)
    return {'nonce': base64.b64encode(nonce).decode(), 'ciphertext': base64.b64encode(ct).decode(), 'ts': datetime.now().isoformat()}

def decrypt_with_master(master_key: bytes, obj):
    aesgcm = AESGCM(master_key)
    nonce = base64.b64decode(obj['nonce'])
    ct = base64.b64decode(obj['ciphertext'])
    pt = aesgcm.decrypt(nonce, ct, None)
    return pt.decode()

def ensure_setup():
    cfg = load_config()
    if cfg is None:
        print("No keystore found — creating a new master key.")
        pwd = input("Set a password (keep it safe): ").strip()
        mk = new_master_key()
        wrapped = wrap_master(mk, pwd)
        cfg = {'wrapped_master': wrapped, 'created_at': datetime.now().isoformat()}
        save_config(cfg)
        print("Keystore created.")
        return mk
    else:
        pwd = input("Enter your password: ").strip()
        try:
            mk = unwrap_master(cfg['wrapped_master'], pwd)
            return mk
        except Exception as e:
            print("Wrong password or corrupted keystore.")
            return None

def add_note(master_key, data, title, content):
    note_id = str(uuid.uuid4())
    version_id = str(uuid.uuid4())
    enc = encrypt_with_master(master_key, content)
    note = data.get(title, {'note_id':note_id, 'versions':[], 'current': None})
    note['versions'].append({'version_id':version_id, **enc})
    note['current'] = version_id
    data[title] = note
    save_data(data)
    print(f"Note '{title}' added (version {version_id}).")

def view_note(master_key, data, title):
    if title not in data:
        print("Note not found.")
        return
    note = data[title]
    cur = note['current']
    for v in note['versions']:
        if v['version_id'] == cur:
            try:
                pt = decrypt_with_master(master_key, v)
                print(f"=== Note: {title} ===\nCreated: {v['ts']}\nContent: {pt}\n" + "="*40)
            except Exception as e:
                print("Decryption failed (tamper or wrong key).")
            return

def list_notes(data):
    if not data:
        print("No notes.")
        return
    print("=== Your Notes ===")
    for title, note in data.items():
        print(f" {title} (versions: {len(note['versions'])}, current: {note['current']})")
    print("="*40)

def history(data, title):
    if title not in data:
        print("Note not found.")
        return
    for v in data[title]['versions']:
        print(f"version_id: {v['version_id']} ts: {v['ts']}")

def restore(data, title, version_id):
    if title not in data:
        print("Note not found.")
        return
    for v in data[title]['versions']:
        if v['version_id']==version_id:
            data[title]['current'] = version_id
            save_data(data)
            print(f"Restored {title} to {version_id}")
            return
    print("Version not found.")

def set_password():
    cfg = load_config()
    if cfg is None:
        print("No keystore.")
        return
    old = input("Enter current password: ").strip()
    try:
        mk = unwrap_master(cfg['wrapped_master'], old)
    except:
        print("Wrong password.")
        return
    new = input("Enter new password: ").strip()
    wrapped = wrap_master(mk, new)
    cfg['wrapped_master'] = wrapped
    save_config(cfg)
    print("Password updated.")

def export_note(data, title, outpath):
    if title not in data:
        print("Note not found.")
        return
    with open(outpath, 'w') as f:
        json.dump(data[title], f)
    print(f"Exported {title} to {outpath}")

def import_note(data, infile):
    with open(infile,'r') as f:
        note = json.load(f)
    title = input("Enter title to import as: ").strip()
    data[title] = note
    save_data(data)
    print(f"Imported as {title}")

def main():
    master_key = ensure_setup()
    if master_key is None:
        return
    data = load_data()
    print("="*50 + "\n SECURE NOTES APP v2\n AES-GCM + Wrapped master key\n" + "="*50)
    while True:
        cmd = input("\nEnter command: ").strip()
        if cmd == 'exit':
            break
        if cmd == 'list':
            list_notes(data)
            continue
        if cmd.startswith('add '):
            parts = cmd[4:].split(' ',1)
            if len(parts)<2:
                print("Usage: add <title> <content>")
                continue
            add_note(master_key, data, parts[0], parts[1])
            continue
        if cmd.startswith('view '):
            view_note(master_key, data, cmd[5:].strip())
            continue
        if cmd.startswith('history '):
            history(data, cmd[8:].strip())
            continue
        if cmd.startswith('restore '):
            parts = cmd[8:].split(' ',1)
            if len(parts)<2:
                print("Usage: restore <title> <version_id>")
                continue
            restore(data, parts[0], parts[1])
            continue
        if cmd == 'set-password':
            set_password()
            continue
        if cmd.startswith('export '):
            parts = cmd[7:].split(' ',1)
            if len(parts)<2:
                print("Usage: export <title> <outpath>")
                continue
            export_note(data, parts[0], parts[1])
            continue
        if cmd.startswith('import '):
            import_note(data, cmd[7:].strip())
            continue
        print("Unknown command.")
if __name__ == '__main__':
    main()
