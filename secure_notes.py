import os
import json
import base64
from datetime import datetime
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

class SecureNotes:
    def __init__(self, data_file="secure_notes.json"):
        self.data_file = data_file
        self.notes = {}
        self.load_notes()
        
    def generate_key(self, password, salt):
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000, backend=default_backend())
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))[:32]
    
    def encrypt_note(self, note_text, password):
        salt = os.urandom(16)
        key = self.generate_key(password, salt)
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(note_text.encode()) + padder.finalize()
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encrypted = cipher.encryptor().update(padded_data) + cipher.encryptor().finalize()
        return {'salt': base64.b64encode(salt).decode(), 'iv': base64.b64encode(iv).decode(), 'encrypted': base64.b64encode(encrypted).decode(), 'timestamp': datetime.now().isoformat()}
    
    def decrypt_note(self, encrypted_note, password):
        salt = base64.b64decode(encrypted_note['salt'])
        iv = base64.b64decode(encrypted_note['iv'])
        encrypted_data = base64.b64decode(encrypted_note['encrypted'])
        key = self.generate_key(password, salt)
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        padded_data = cipher.decryptor().update(encrypted_data) + cipher.decryptor().finalize()
        unpadder = padding.PKCS7(128).unpadder()
        return (unpadder.update(padded_data) + unpadder.finalize()).decode()
    
    def add_note(self, title, content, password):
        self.notes[title] = {'content': self.encrypt_note(content, password), 'created': datetime.now().isoformat()}
        self.save_notes()
        print(f"Note '{title}' added successfully!")
    
    def view_note(self, title, password):
        if title not in self.notes:
            print(f"Note '{title}' not found!")
            return
        try:
            decrypted = self.decrypt_note(self.notes[title]['content'], password)
            print(f"\n=== Note: {title} ===\nCreated: {self.notes[title]['created']}\nContent: {decrypted}\n" + "="*40)
        except:
            print("Wrong password or corrupted data!")
    
    def list_notes(self):
        if not self.notes:
            print("No notes found!")
            return
        print("\n=== Your Notes ===")
        for title, data in self.notes.items():
            print(f"  {title} (created: {data['created']})")
        print("="*40)
    
    def delete_note(self, title):
        if title not in self.notes:
            print(f"Note '{title}' not found!")
            return
        del self.notes[title]
        self.save_notes()
        print(f"Note '{title}' deleted!")
    
    def save_notes(self):
        with open(self.data_file, 'w') as f:
            json.dump(self.notes, f)
    
    def load_notes(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                self.notes = json.load(f)

def main():
    notes = SecureNotes()
    print("="*50 + "\n       SECURE NOTES APP\n       AES-256 Encrypted Storage\n" + "="*50)
    while True:
        print("\nCommands: add <title> <content> | view <title> | list | delete <title> | exit")
        cmd = input("\nEnter command: ").strip()
        if cmd.lower() == 'exit':
            print("Exiting...")
            break
        elif cmd.lower() == 'list':
            notes.list_notes()
        elif cmd.lower().startswith('add '):
            parts = cmd[4:].split(' ', 1)
            if len(parts) < 2:
                print("Usage: add <title> <content>")
            else:
                pwd = input("Enter encryption password: ").strip()
                if pwd:
                    notes.add_note(parts[0], parts[1], pwd)
        elif cmd.lower().startswith('view '):
            title = cmd[5:].strip()
            if title:
                pwd = input("Enter decryption password: ").strip()
                notes.view_note(title, pwd)
        elif cmd.lower().startswith('delete '):
            notes.delete_note(cmd[7:].strip())
        else:
            print("Unknown command!")

if __name__ == "__main__":
    main()
