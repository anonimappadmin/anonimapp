# Anonimapp

Anonimapp is a privacy-first messaging platform that allows users to create anonymous, self-destructing voice and text messages. Designed for whistleblowers, vulnerable individuals, or anyone needing to share sensitive information without leaving a trace, Anonimapp prioritizes confidentiality, one-time access, and zero personal data collection.

---

## 🚀 Core Features

- 🕵️ Anonymous Message Creation (Text + Voice)
- 🔐 Access via One-Time Keys (3 unique keys per message)
- 🧨 Self-destructing logic (after 3 views or 30 seconds)
- 📦 No login, email, or user tracking
- 📤 Shareable via secure link + QR code
- 🎙️ Voice messages supported with auto-expiration
- 🛡️ Reported messages can be flagged and reviewed

---

## 📌 Use Cases

- **Whistleblowing**
- **Abuse Reporting**
- **Mental Health Confessions**
- **Anonymous Tips**
- **Time-sensitive Secrets**

---

## 🧠 How It Works

### 1. Creating a Message
Users can write a message or record a voice note. Once submitted, Anonimapp:
- Generates a `message_id`
- Stores the content in a local SQLite database
- Generates 3 one-time-use access keys
- Creates a QR code + shareable link for access

### 2. Accessing a Message
The recipient enters one of the 3 access keys:
- If valid and unused, the message opens
- Views are decremented; keys are marked used
- After 3 total views OR 30 seconds (whichever is sooner), the message expires

### 3. Voice Messages
Voice notes are saved as `.webm` files and follow the same key and expiration logic as text messages.

---

## ⚙️ Tech Stack

| Layer              | Technology                    |
|--------------------|-------------------------------|
| Backend            | Python + Flask                |
| Frontend           | HTML + Bootstrap              |
| Database           | SQLite(dev) + PostgreSQL(prod)|
| Audio Handling     | Web Audio API                 |
| QR Generation      | `qrcode` Python lib           |
| Access Control     | Unique UUID Keys              |
| Hosting (Planned)  | Railway / Render              |

---

## 🔒 Security Considerations

- No user accounts or IP tracking
- All keys are stored securely and marked as "used" upon access
- Keys expire after one-time use
- Messages auto-destruct after 3 views or 30 seconds
- File uploads limited to 10MB for voice
- Admin moderation tools available for reported content

---

## 🧪 Local Setup (Development)

1. **Clone the Repo**
   ```bash
   git clone https://github.com/anonimappadmin/anonimapp.git
   cd anonimapp

2. **Create Virtual Environment
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

3. **Install Dependencies
   ```bash
   pip install -r requirements.txt

4. **Run Locally - a
   ```bash
   python app.py

5. **Run Locally - b
   ```bash
   flask run

6. **Then open your browser at:
   ```cpp
   http://127.0.0.1:5000

7. **Deployment - Recommended Platforms
   * Railway.app
   * Render.com
   * Fly.io

## Setup Notes
   * Store secrects in .env file:
      * FLASK_SECRET_KEY=your_secret_here
   * Limit audio file size and validate uploads.
   * Switch from SQLite to PostgreSQL for scalability:
      * Suggested migratin path: SQALchemy ORM

## 🛡️ Security Considerations
- No authentication required = no user data stored
- One-time keys prevent replay attacks
- Views and expiration timers eliminate persistent storage
- Voice files are deleted after expiration (auto-cleanup pending)
- Upload size limits help prevent abuse

## 📁 Project Structure
```csharp
anonimapp/
│
├── app.py               # Main application
├── database.py          # DB logic and helpers
├── create_admin.py      # Add admin account
├── static/              # Assets (QR codes, audio files)
│   ├── voices/
│   └── qr/
├── templates/           # Jinja2 HTML templates
├── requirements.txt     # Python dependencies
├── anonimapp.db         # SQLite database (local)
└── README.md

## 📜 License


  
