import sqlite3
from werkzeug.security import generate_password_hash

DB_PATH = 'anonimapp.db'  # Update if your DB path is different

def create_admin(username, password):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    hashed_password = generate_password_hash(password)
    try:
        c.execute('INSERT INTO admin (username, password) VALUES (?, ?)', (username, hashed_password))
        conn.commit()
        print(f"Admin '{username}' created successfully.")
    except sqlite3.IntegrityError:
        print("Error: Admin with that username already exists.")
    finally:
        conn.close()

def log_admin_action(username, action, message_id=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO admin_logs (admin_username, action, message_id)
        VALUES (?, ?, ?)
    ''', (username, action, message_id))
    conn.commit()
    conn.close()


# Run this
if __name__ == '__main__':
    user = input("Enter admin username: ")
    pwd = input("Enter admin password: ")
    create_admin(user, pwd)
