<<<<<<< HEAD
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
- **Violence and Abuse Reporting**
- **Mental Health Confessions**
- **Anonymous Tips**
- **Time-sensitive Secrets**
- **Human Rights Abuses**
- **Political and Religious Persecutions**

---

## 🔐 Additional Elaborated Use Cases
- Apologies or Final Words - Leaving a message that can’t be traced back, especially for unresolved conflicts or closure.
- Anonymous Feedback in the Workplace - Letting employees or students send messages without fear of retaliation.
- Coming Out Stories - For people who want to express their identity safely without revealing their identity.
- End-of-Life Messages - Private thoughts or messages saved for specific individuals, accessible only with a key.
- Romantic Confessions - A way to say something difficult or unspoken, without the weight of being known.
- Sharing Evidence Without a Trail - Recordings, or testimonies shared securely without metadata trails.
- Activist Communications - Exchanging sensitive info while protecting sender identity under oppressive regimes.
- Custody or Family Disputes - Messages that must be heard but can't be reused in court or outside context.
- And more...

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

2. Create Virtual Environment
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

3. Install Dependencies
   ```bash
   pip install -r requirements.txt

4. Run Locally - a
   ```bash
   python app.py

5. Run Locally - b
   ```bash
   flask run

6. Then open your browser at:
   ```cpp
   http://127.0.0.1:5000

## ☁️ Deployment - Recommended Platforms
   * Railway.app
   * Render.com
   * Fly.io

## Setup Notes
   * Store secrects in .env file:
      * FLASK_SECRET_KEY=your_secret_here
   * Limit audio file size and validate uploads.
   * Switch from SQLite to PostgreSQL for scalability:
      * Suggested migratin path: SQALchemy ORM
     

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
---

## 📜 License

This project is released under the MIT License.
=======
Anonimapp

Anonimapp is a minimalist, privacy-focused communication platform for sending self-destructing text and voice messages anonymously. It is designed to enable people to speak freely without the fear of their message being traced, archived, or shared outside its intended context.

Table of Contents

Overview

Core Features

Technical Architecture

How It Works

Security Considerations

Project Structure

Local Setup

Deployment

License

Overview

Anonimapp addresses the growing need for secure, ephemeral messaging by enabling anyone to send a private message or voice note that can only be viewed with a single-use access key. Messages automatically self-destruct after either 3 views or 30 seconds, whichever comes first.

Core Features

Anonymous Text Messaging: Write and share a message without logging in or creating an account.

Anonymous Voice Recording: Record short voice notes (max 60s) directly in the browser.

Ephemeral Delivery: All messages expire after 3 views or 30 seconds.

Access Control via Keys: Every message generates 3 random access keys that must be used to unlock it.

No Tracking: No user data, no cookies, no analytics.

QR Code Sharing: Every message generates a scannable QR code for easy sharing.

Technical Architecture

Frontend: HTML, Bootstrap 5, and Vanilla JS

Backend: Python Flask

Database: SQLite (development), Postgres (recommended for production)

Media Handling: HTML5 MediaRecorder API + Flask file handling for voice recording

Key Security: Single-use access keys stored and tracked in an access_keys table

How It Works

Text Messages

User writes and submits a message.

System stores the message with an auto-generated UUID.

Three unique access keys are generated and stored with usage flags.

The user receives a link, QR code, and the 3 keys.

The message can only be viewed using one of those keys.

Upon access, the key is marked as used and the view count is decremented.

The message auto-expires after 3 views or 30 seconds.

Voice Messages

The user records a message in-browser.

The recording is uploaded as a .webm file to the server.

Metadata is stored in the messages table with a UUID.

The same 3-access key mechanism applies.

Playback is only possible with a valid, unused key.

Voice notes are deleted after expiration logic is satisfied.

Security Considerations

Single-Use Keys: Prevent replays or accidental multiple views.

Self-Destruction: Ensures messages cannot linger indefinitely.

No User Accounts: Eliminates the need to manage sensitive user data.

Input Filtering: Future-proofing needed for uploads and malicious text.

Rate Limiting: To be enforced via Flask-Limiter or similar in production.

Voice File Cleanup: Recommended cron or background task for pruning expired audio/QRs.

Project Structure

anonimapp/
├── app.py                  # Main Flask application
├── database.py             # SQLite/Postgres interaction logic
├── templates/              # Jinja2 templates for all pages
├── static/                 # Static assets (CSS, JS, uploaded files)
├── .gitignore              # File exclusions
├── requirements.txt        # Project dependencies
├── README.md               # This file
└── anonimapp.db            # Local DB (excluded from Git)

Local Setup

Clone the Repo

git clone https://github.com/YOUR_USERNAME/anonimapp.git
cd anonimapp

Create Virtual Environment

python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

Install Dependencies

pip install -r requirements.txt

Run Locally

python app.py

Visit http://127.0.0.1:5000 in your browser.

Deployment

Recommended platforms:

Railway.app

Render.com

Fly.io

Setup Notes:

Use a .env file to set your Flask secret and other config vars.

Switch to Postgres and use SQLAlchemy for production-ready DB support.

Limit file sizes and enforce upload constraints.

License

This project is released under the MIT License.

>>>>>>> 06550b0 (Add initial README for Anonimapp)
