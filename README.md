# 🔐 Secure Notes App

A secure, encrypted notes application built with Streamlit. It uses PBKDF2 key derivation and AES-GCM encryption to store private notes locally with strong password-based protection.

## ✨ Features

| Feature | Description |
|---|---|
| 🔒 Password Unlock | Lock and unlock the app with a user password |
| 🔐 PBKDF2 Key Derivation | Derives encryption keys from the password using PBKDF2-HMAC-SHA256 |
| 🎲 Unique Salt & Nonce | Each keystore and note uses random cryptographic values |
| 💾 Local Storage | Notes are stored locally in JSON format |
| 🛡️ Offline First | Works without cloud dependency |
| ⌨️ Streamlit UI | Easy web-based interface instead of CLI |
| 🕘 Version History | Keep and restore previous versions of notes |
| 📦 Import / Export | Transfer encrypted notes using JSON files |
| 🧩 Biometric Tab | Placeholder for Windows-based biometric integration |



## 🚀 Installation

### Prerequisites

- Python 3.x installed
  
- Git (optional, for version control)



### Setup

```powershell
cd secure_notes_app

pip install streamlit cryptography requests flask
```

## 📖 Usage

### Start the App

```powershell
streamlit run .\secure_notes_streamlit_app.py
```

### First Run

1. Open the app in your browser.
2. Create a keystore using your password.
3. Unlock the app with the same password.
4. Add, view, and manage encrypted notes.

## 🧭 App Features

### Add Note
- Enter a title.
- Write your note content.
- Save it encrypted with your password-derived key.

### View Notes
- Select a note.
- Decrypt and read the saved content.

### History
- See older encrypted versions of a note.
- Restore a previous version by version ID.

### Sync
- Download encrypted JSON.
- Import encrypted JSON from another device.
- Optional sync server support can be added later.

### Biometric
- Shows biometric availability on Windows.
- Can be extended to use Windows Hello or a compatible biometric wrapper.

## 💡 Example Workflow

```text
Open the app
Create Keystore
Enter password: mysecurepassword123
Unlocked.

Add Note
Title: diary
Content: My secret thoughts about quantum security project
Saved version ...

View Notes
Select note: diary
Decrypt Selected Note
Content: My secret thoughts about quantum security project
```

## 📁 Project Structure

```text
secure_notes_app/
├─ secure_notes_streamlit_app.py
├─ features/
│  ├─ biometric.py
│  ├─ sync_client.py
│  └─ versioning.py
├─ backend/
│  └─ sync_server.py
├─ keystore_streamlit.json
├─ secure_notes_streamlit.json
├─ versions_streamlit.json
└─ README.md
```

## 🔒 Security Notes

- Passwords are never stored directly.
- PBKDF2 is used to derive a key from the password.
- AES-GCM is used to encrypt note content.
- Each keystore uses a random salt.
- Each note uses a random nonce.
- Local JSON files should be excluded from GitHub commits.

## 🚧 What Is Still Limited

- Biometric unlock is not fully native inside Streamlit.
- Cloud sync is only ready in format through encrypted export/import.
- Multi-device provisioning still needs a proper backend or secure key-sharing flow.
- Remote version history sync is not yet connected to a server.

## 📜 License

This project is open source. Feel free to use and modify.

## 👨‍💻 Author

**Siri Mudaddla**

GitHub: [SiriMudaddla](https://github.com/SiriMudaddla)

## 🙏 Acknowledgments

Built with Python's `cryptography` library using:

- PBKDF2-HMAC-SHA256 for key derivation
- AES-GCM for encryption and integrity protection
- Streamlit for the user interface
