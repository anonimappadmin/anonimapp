import os
import sqlite3
import uuid
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_cors import CORS
from werkzeug.security import check_password_hash
import qrcode
import humanize
import database  # Do not import log_admin_action from here
from database import get_message_by_id, decrement_views, get_admin_by_username, safe_db_execute
from functools import wraps
import secrets
from flask import jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address



app = Flask(__name__)
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["100 per hour"]  # Optional: global default
)

app.secret_key = os.environ.get("FLASK_SECRET_KEY", "anonimapp-secret")
CORS(app)
DB_FILE = 'anonimapp.db'
DB_PATH = os.path.join(os.path.dirname(__file__), DB_FILE)
UPLOAD_FOLDER = os.path.join('static', 'voices')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024


@limiter.request_filter
def exempt_static_files():
    return request.path.startswith('/static/')

@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify(error="Too many requests, please slow down."), 429

def log_admin_action(username, action, message_id=None):
    safe_db_execute('''
        INSERT INTO admin_logs (admin_username, action, message_id)
        VALUES (?, ?, ?)
    ''', (username, action, message_id))

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            flash("You must be logged in as admin to access this page.")
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function


def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute('PRAGMA journal_mode=WAL;')
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                content TEXT,
                label TEXT,
                is_voice INTEGER DEFAULT 0,
                views_remaining INTEGER DEFAULT 3,
                is_public INTEGER DEFAULT 0,
                created_at TEXT DEFAULT (datetime('now')),
                viewed_at TEXT DEFAULT NULL
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS access_keys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id TEXT,
                key TEXT,
                used INTEGER DEFAULT 0
            )
        ''')

@app.template_filter('humantime')
def humantime(value):
    if not value:
        return "unknown"
    dt = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
    now = datetime.utcnow()
    diff = now - dt
    seconds = diff.total_seconds()
    if seconds < 60:
        return "just now"
    elif seconds < 3600:
        return f"{int(seconds / 60)} minute(s) ago"
    elif seconds < 86400:
        return f"{int(seconds / 3600)} hour(s) ago"
    elif seconds < 604800:
        return f"{int(seconds / 86400)} day(s) ago"
    else:
        return dt.strftime("%b %d, %Y - %I:%M %p")

@app.route('/')
def index():
    try:
        public_messages = database.get_public_messages()
        return render_template('landing.html', public_messages=public_messages, now=datetime.utcnow())
    except Exception as e:
        app.logger.error(f"Index route error: {e}")
        flash("Something went wrong loading the homepage.", "danger")
        return render_template('landing.html', public_messages=[], now=datetime.utcnow())

@limiter.limit("5 per minute")
@app.route('/submit', methods=['GET', 'POST'])
def submit():
    if request.method == 'POST':
        label = request.form.get('label', '')
        content = request.form['message']
        message_id = str(uuid.uuid4())
        database.save_message(content, label=label, key=message_id)

        #flash(f"Private message created. Access key: {access_key}", 'info')
        return redirect(url_for('share_message', message_id=message_id))

    return render_template('submit.html')







'''@app.route('/access_voice', methods=['GET', 'POST'])
def access_voice():
    if request.method == 'POST':
        try:
            key = request.form['voice_key']
            voice_id = database.validate_key(None, key, require_voice=True)
            if voice_id:
                return redirect(url_for('play_voice', voice_id=voice_id))
            else:
                flash("Invalid or already used key.", "danger")
        except Exception as e:
            app.logger.error(f"Access voice error: {e}")
            flash("An error occurred accessing the voice message.", "danger")
    return render_template('access_voice.html')'''


@limiter.limit("3 per minute")
@app.route('/access_key', methods=['GET', 'POST'])
def access_key():
    if request.method == 'POST':
        key = request.form.get('message_key', '').strip()

        if not key:
            flash("Please enter a valid key.")
            return render_template("access_key.html")

        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                # Get the message_id and type
                cursor.execute("SELECT message_id FROM access_keys WHERE key = ? AND used = 0", (key,))
                row = cursor.fetchone()

                if not row:
                    flash("Invalid or already used key.")
                    return render_template("access_key.html")

                message_id = row[0]

                # Get the is_voice flag
                cursor.execute("SELECT is_voice FROM messages WHERE id = ?", (message_id,))
                msg = cursor.fetchone()

                if not msg:
                    flash("Message not found.")
                    return render_template("access_key.html")

                is_voice = msg[0]

                # Mark key as used
                cursor.execute("UPDATE access_keys SET used = 1 WHERE key = ?", (key,))
                conn.commit()

            # Redirect to the appropriate route
            if is_voice == 1:
                return redirect(url_for('play_voice', voice_id=message_id))
            else:
                return redirect(url_for('view_message', message_id=message_id))

        except Exception as e:
            app.logger.error(f"Access key error: {e}")
            flash("An error occurred while accessing your message.")
            return render_template("access_key.html")

    return render_template("access_key.html")



@app.route('/view/<message_id>')
def view_message(message_id):
    message = get_message_by_id(message_id)
    
    if not message:
        flash("Message not found.")
        return redirect(url_for('my_messages'))

    # Check if expired by views or time
    views_remaining = message['views_remaining']
    created_at = datetime.strptime(message['created_at'], "%Y-%m-%d %H:%M:%S")
    expires_at = created_at + timedelta(seconds=30)
    time_left = (expires_at - datetime.utcnow()).total_seconds()

    if views_remaining <= 0 or time_left <= 0:
        return render_template('expired.html')

    # Decrement views and render message
    decrement_views(message_id)
    return render_template('view_message.html', message=message['content'], seconds_remaining=int(time_left), message_id=message_id)

@app.route('/report/<message_id>', methods=['POST'])
def report_message(message_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE messages SET is_reported = 1 WHERE id = ?", (message_id,))
    conn.commit()
    conn.close()

    flash("Message has been reported. Thank you.", "warning")
    return redirect(url_for('my_messages'))

@limiter.limit("5 per minute")
@app.route('/upload_voice', methods=['POST'])
def upload_voice():
    try:
        file = request.files['audio_data']
        user_key = request.form.get('access_key', '').strip() or None

        if file:
            voice_id = str(uuid.uuid4())[:8]
            filename = f"{voice_id}.webm"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            access_key = user_key or secrets.token_urlsafe(8)

            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO messages (
                        id, content, label, is_voice, views_remaining, is_public, created_at, viewed_at
                    ) VALUES (?, ?, ?, ?, ?, ?, datetime('now'), NULL)
                """, (voice_id, None, None, 1, 3, 0))
                conn.commit()


            # ✅ Generate 3 access keys only once
            database.create_keys_for_message(voice_id)

            return jsonify({'voice_id': voice_id}), 200

        return "Upload failed", 400

    except Exception as e:
        app.logger.error(f"Upload voice error: {e}")
        return "Server error.", 500



            

        return "Upload failed", 400

    except Exception as e:
        app.logger.error(f"Upload voice error: {e}")
        return "Server error.", 500




@app.route('/share/<message_id>')
def share_message(message_id):
    message = database.get_message_by_id(message_id)
    if not message:
        flash("Message not found.", "danger")
        return redirect(url_for('submit'))

    # ✅ Check for existing keys first
    access_keys = database.get_keys_for_message(message_id)

    # 🔐 Only generate new keys if NONE exist
    if not access_keys:
        database.create_keys_for_message(message_id)  # Should create exactly 3
        access_keys = database.get_keys_for_message(message_id)  # Re-fetch to display

    # 🔗 Link + QR
    link = url_for('view_message', message_id=message_id, _external=True)
    qr_img = qrcode.make(link)
    qr_path = os.path.join('static', 'qr', f"{message_id}.png")
    qr_img.save(qr_path)

    return render_template('share.html', link=link, qr_filename=f"{message_id}.png", access_keys=access_keys)



@app.route('/play_voice/<voice_id>', methods=['GET', 'POST'])
def play_voice(voice_id):
    try:
        if request.method == 'POST':
            key = request.form.get('voice_key')
            valid, error = database.validate_and_use_key(voice_id, key)
            if not valid:
                flash(error, 'danger')
                return redirect(url_for('access_voice'))

        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT views_remaining FROM messages WHERE id = ?", (voice_id,))
            result = cursor.fetchone()

            if result:
                views = result[0]
                if views <= 0:
                    return render_template('expired.html'), 410

                cursor.execute("UPDATE messages SET views_remaining = views_remaining - 1 WHERE id = ?", (voice_id,))
                conn.commit()

                filename = f"{voice_id}.webm"
                return render_template('play_voice.html', voice_file=filename, views_remaining=views - 1)
            return "Voice message not found", 404
    except Exception as e:
        app.logger.error(f"Play voice error: {e}")
        return "Server error.", 500

@app.route('/my_messages')
def my_messages():
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, label, content, is_voice, views_remaining, created_at FROM messages ORDER BY created_at DESC")
            messages = cursor.fetchall()
        return render_template('my_messages.html', messages=messages)
    except Exception as e:
        import traceback
        print("ERROR in /my_messages:", e)
        traceback.print_exc()
        app.logger.error(f"My messages error: {e}")
        flash("Failed to load your messages.", "danger")
        return render_template('my_messages.html', messages=[])
    
@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/donate')
def donate():
    return render_template('donate.html')

@app.route('/why_it_matters')
def it_matters():
    return render_template('why_it_matters.html')

@app.route('/terms_of_use')
def terms_of_use():
    return render_template('terms_of_use.html')

@app.route('/help')
def help():
    return render_template('help.html')

@app.route('/faqs')
def faqs():
    return render_template('faqs.html')

'''@app.route('/access_message', methods=['GET', 'POST'])
def access_message():
    if request.method == 'POST':
        key = request.form.get('message_key', '').strip()
        if not key:
            flash("Please enter a valid key.")
            return render_template("access_message.html")

        message_id = database.validate_key(None, key)
        if not message_id:
            flash("Invalid or already used key.")
            return render_template("access_message.html")

        # Redirect based on whether it’s text or voice
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT is_voice FROM messages WHERE id = ?", (message_id,))
            result = cursor.fetchone()
            if result and result[0] == 1:
                return redirect(url_for('play_voice', voice_id=message_id))
            else:
                return redirect(url_for('view_message', message_id=message_id))

    return render_template("access_message.html")'''


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        admin = get_admin_by_username(username)

        if admin and check_password_hash(admin[2], password):  # admin[2] = hashed password
            session['admin_logged_in'] = True
            session['admin_username'] = admin[1]
            flash('Logged in successfully!')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials. Please try again.')

    return render_template('admin.html')  # This is your login form

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    try:
        filter_type = request.args.get('type')
        date_filter = request.args.get('date_filter')

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        # Base query
        query = "SELECT * FROM messages WHERE is_reported = 1"
        params = []

        if filter_type == "text":
            query += " AND is_voice = 0"
        elif filter_type == "voice":
            query += " AND is_voice = 1"

        if date_filter == "24h":
            query += " AND created_at >= datetime('now', '-1 day')"
        elif date_filter == "7d":
            query += " AND created_at >= datetime('now', '-7 days')"
        elif date_filter == "30d":
            query += " AND created_at >= datetime('now', '-30 days')"
        elif date_filter == "12m":
            query += " AND created_at >= datetime('now', '-12 months')"

        query += " ORDER BY created_at DESC"
        c.execute(query, params)
        messages = c.fetchall()

        # --- STATS SECTION ---

        # Total messages
        c.execute("SELECT COUNT(*) FROM messages")
        total_messages = c.fetchone()[0]

        # Reported messages
        c.execute("SELECT COUNT(*) FROM messages WHERE is_reported = 1")
        reported_messages = c.fetchone()[0]

        # Voice messages
        c.execute("SELECT COUNT(*) FROM messages WHERE is_voice = 1")
        total_voice_messages = c.fetchone()[0]

        # Active users (rough estimate: unique message IDs)
        c.execute("SELECT COUNT(DISTINCT id) FROM messages")
        active_users = c.fetchone()[0]

        # Active messages (views > 0 and not expired)
        c.execute("""
            SELECT COUNT(*) FROM messages
            WHERE views_remaining > 0 AND (strftime('%s', expires_at) > strftime('%s', 'now'))
        """)
        active_messages = c.fetchone()[0]

        # Chart data: last 14 days
        c.execute("""
            SELECT strftime('%Y-%m-%d', created_at) as date, COUNT(*) 
            FROM messages 
            GROUP BY date 
            ORDER BY date DESC 
            LIMIT 14
        """)
        rows = c.fetchall()
        rows.reverse()

        chart_labels = [row[0] for row in rows]
        chart_data = [row[1] for row in rows]

        conn.close()

        return render_template(
            'admin_dashboard.html',
            messages=messages,
            total_messages=total_messages,
            total_voice_messages=total_voice_messages,
            active_messages=active_messages,
            reported_messages=reported_messages,
            active_users=active_users,
            chart_labels=chart_labels,
            chart_data=chart_data
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"Server error: {str(e)}", 500


@app.route('/admin/view/<message_id>')
@admin_required
def view_message_admin(message_id):
    message = get_message_by_id(message_id)
    if not message:
        flash("Message not found.")
        return redirect(url_for('admin_dashboard'))
    
        
    log_admin_action(session.get('admin_username'), 'Viewed message', message_id)
    return render_template('view_message.html', message=message[1])  # content at index 1


@app.route('/admin/delete/<message_id>')
@admin_required
def admin_delete(message_id):
    from database import log_admin_action  # import here only when needed

    delete_message(message_id)
    log_admin_action(session['admin_username'], "delete", message_id)
    flash("Message deleted.")
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/logs')
@admin_required
def admin_logs():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM admin_logs ORDER BY timestamp DESC')
    logs = c.fetchall()
    conn.close()
    return render_template('admin_logs.html', logs=logs)


@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    session.pop('admin_username', None)
    flash('You’ve been logged out.')
    return redirect(url_for('admin_login'))

@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

print(app.url_map)

