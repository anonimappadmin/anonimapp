import sqlite3
import uuid
import os
from werkzeug.security import generate_password_hash
import time

DB_FILE = 'anonimapp.db'
# Define path to your database file
DB_PATH = os.path.join(os.path.dirname(__file__), 'anonimapp.db')

def connect():
    return sqlite3.connect('anonimapp.db')



def safe_db_execute(query, params=(), fetch=False):
    attempts = 0
    while attempts < 5:
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                if fetch:
                    return cursor.fetchall()
                conn.commit()
                return True
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                time.sleep(0.3)
                attempts += 1
            else:
                raise
    raise Exception("Database locked too long.")


def init_db():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id TEXT PRIMARY KEY,
            content TEXT,
            is_voice INTEGER DEFAULT 0,
            views_remaining INTEGER DEFAULT 3,
            is_public INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now'))
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS access_keys (
            key TEXT PRIMARY KEY,
            message_id TEXT,
            used INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def get_public_messages():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, content, views_remaining, is_voice, created_at 
        FROM messages 
        WHERE is_public = 1 
        ORDER BY id DESC
    """)
    messages = cursor.fetchall()
    conn.close()
    return messages
    
def save_message(content, label='', key=None):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO messages (
                id, content, label, is_voice, views_remaining, is_public, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
        """, (key, content, label, 0, 3, 0))
        conn.commit()


def decrement_views(message_id):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("UPDATE messages SET views_remaining = views_remaining - 1 WHERE id = ?", (message_id,))
    conn.commit()
    conn.close()

def get_message_by_id(message_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('''
        SELECT id, content, label, is_voice, views_remaining, created_at
        FROM messages WHERE id = ?
    ''', (message_id,))
    result = c.fetchone()
    conn.close()
    return result


def create_keys_for_message(message_id):
    with sqlite3.connect('anonimapp.db') as conn:
        cursor = conn.cursor()
        for _ in range(3):  # create 3 keys
            key = str(uuid.uuid4())[:8]
            cursor.execute("INSERT INTO access_keys (message_id, key, used) VALUES (?, ?, 0)", (message_id, key))
        conn.commit()

def get_keys_for_message(message_id):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT key FROM access_keys WHERE message_id = ?", (message_id,))
        return cursor.fetchall()


def validate_key(message_id, submitted_key):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT used FROM access_keys WHERE key = ? AND message_id = ?", (submitted_key, message_id))
    row = cursor.fetchone()

    if not row:
        return False, "Invalid key"
    elif row[0] == 1:
        return False, "Key already used"

    cursor.execute("UPDATE access_keys SET used = 1 WHERE key = ?", (submitted_key,))
    cursor.execute("UPDATE messages SET views_remaining = views_remaining - 1 WHERE id = ?", (message_id,))
    conn.commit()
    conn.close()
    return True, "Access granted"

def validate_and_use_key(message_id, provided_key):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT used FROM message_keys
        WHERE key = ? AND message_id = ?
    """, (provided_key, message_id))
    result = cursor.fetchone()

    if not result:
        conn.close()
        return False, "Invalid or non-existent key."

    used = result[0]
    if used:
        conn.close()
        return False, "This key has already been used."
    
def create_admin(username, password):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    hashed_pw = generate_password_hash(password)
    try:
        c.execute("INSERT INTO admin (username, password) VALUES (?, ?)", (username, hashed_pw))
        conn.commit()
    except sqlite3.IntegrityError:
        return False  # Username already exists
    finally:
        conn.close()
    return True

def get_admin_by_username(username):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM admin WHERE username = ?", (username,))
    admin = c.fetchone()
    conn.close()
    return admin

    # Mark key as used
    cursor.execute("UPDATE message_keys SET used = 1 WHERE key = ?", (provided_key,))
    conn.commit()
    conn.close()
    return True, None

