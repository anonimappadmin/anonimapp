import sqlite3

DB_PATH = 'anonimapp.db'  # or full path if different

def reset_messages_table():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # DROP TABLE if exists
    c.execute("DROP TABLE IF EXISTS messages")

    # RECREATE with correct schema
    c.execute('''
        CREATE TABLE messages (
            id TEXT PRIMARY KEY,
            content TEXT,
            label TEXT,
            is_voice INTEGER DEFAULT 0,
            views_remaining INTEGER DEFAULT 3,
            is_public INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now')),
            viewed_at TEXT DEFAULT NULL,
            is_reported INTEGER DEFAULT 0,
            expires_at TEXT
        )
    ''')

    conn.commit()
    conn.close()
    print("✅ messages table reset and recreated successfully.")

if __name__ == "__main__":
    reset_messages_table()
