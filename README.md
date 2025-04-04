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

