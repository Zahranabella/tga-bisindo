import sqlite3
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row  # Agar bisa akses kolom seperti dictionary
    return conn

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

def simpan_riwayat(username, original_video_path, processed_video_path, detected_labels):
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO history (username, original_video, processed_video, detected_labels) VALUES (?, ?, ?, ?)",
        (username, original_video_path, processed_video_path, detected_labels)
    )
    conn.commit()
    conn.close()

def get_user_history(username):
    conn = get_db_connection()
    history = conn.execute(
        "SELECT * FROM history WHERE username = ? ORDER BY created_at DESC",
        (username,)
    ).fetchall()
    conn.close()
    return history

def hapus_riwayat_by_id(riwayat_id, username):
    conn = get_db_connection()
    conn.execute("DELETE FROM history WHERE id = ? AND username = ?", (riwayat_id, username))
    conn.commit()
    conn.close()