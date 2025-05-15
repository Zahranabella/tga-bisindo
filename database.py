import sqlite3

DB_NAME = 'database.db'

def create_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL
                )''')
    conn.commit()
    conn.close()

def add_user(username, password_plain):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute("INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)", (username, password_plain))
        conn.commit()
        print(f"User '{username}' ditambahkan.")
    except sqlite3.IntegrityError:
        print("Username sudah ada.")
    conn.close()

def get_user(username):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    conn.close()
    return user
