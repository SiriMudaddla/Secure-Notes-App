# 🔐 Secure Notes App

A secure, encrypted notes application with **AES-256-CBC encryption** and **PBKDF2 key derivation**. Store your private notes locally with military-grade encryption.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔒 **AES-256-CBC Encryption** | All notes encrypted with industry-standard AES-256 |
| 🔐 **PBKDF2 Key Derivation** | 100,000 iterations for strong password hashing |
| 🎲 **Unique Salt & IV** | Each note has its own random salt and initialization vector |
| 💾 **Local Storage** | Notes stored in JSON format on your device |
| 🛡️ **100% Offline** | No cloud dependency - full privacy control |
| ⌨️ **Simple CLI** | Easy command-line interface |

---

## 🚀 Installation

### Prerequisites
- Python 3.x installed
- Git (optional, for version control)

### Setup

```bash
# Navigate to project directory
cd secure_notes_app

# Install dependencies
pip install cryptography
```

---

## 📖 Usage

### Start the App

```bash
python secure_notes.py
```

### Available Commands

| Command | Description | Example |
|---------|-------------|---------|
| `add <title> <content>` | Add a new encrypted note | `add diary "My secret thoughts"` |
| `view <title>` | View a decrypted note | `view diary` |
| `list` | List all notes | `list` |
| `delete <title>` | Delete a note | `delete diary` |
| `exit` | Exit the app | `exit` |

---

## 💡 Example Workflow
Enter command: add diary "My secret thoughts about quantum security project"
Enter encryption password: mysecurepassword123
Note 'diary' added successfully!

Enter command: add meeting "Discuss Shor's algorithm and differential privacy"
Enter encryption password: mysecurepassword123
Note 'meeting' added successfully!

Enter command: list

=== Your Notes ===

diary (created: 2026-06-21T16:00:00)

meeting (created: 2026-06-21T16:01:30)
================================================

Enter command: view diary

Enter decryption password: mysecurepassword123

=== Note: diary ===

Created: 2026-06-21T16:00:00

Content: My secret thoughts about quantum security project
========================================

Enter command: exit

Exiting...

📜 License

This project is open source. Feel free to use and modify.

---

## 👨‍💻 Author

**Siri Mudaddla**  

Github:https://github.com/SiriMudaddla

---

## 🙏 Acknowledgments

Built with Python's `cryptography` library using:

- AES-256-CBC for encryption
  
- PBKDF2-HMAC-SHA256 for key derivation
