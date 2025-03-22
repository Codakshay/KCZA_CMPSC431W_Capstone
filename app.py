from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import hashlib

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with your secret key for session management
DATABASE = 'users.db'

def hash_password(password: str) -> str:
    """Securely hash the provided password using SHA256."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def create_users_table():
    """Create the users table if it doesn't already exist."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            hashed_password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def register_user(email: str, password: str) -> bool:
    """Register a new user by inserting their email and hashed password."""
    hashed_pwd = hash_password(password)
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (email, hashed_password) VALUES (?, ?)", (email, hashed_pwd))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # Email already exists
    finally:
        conn.close()

def authenticate_user(email: str, password: str) -> bool:
    """Authenticate a user by comparing the hash of the provided password with the stored hash."""
    hashed_input = hash_password(password)
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT hashed_password FROM users WHERE email = ?", (email,))
    result = cursor.fetchone()
    conn.close()
    if result is None:
        return False
    stored_hash = result[0]
    return stored_hash == hashed_input

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    email = request.form.get('email')
    password = request.form.get('password')
    if register_user(email, password):
        flash("Registration successful. You can now log in.")
    else:
        flash("Registration failed. Email already exists.")
    return redirect(url_for('index'))

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    if authenticate_user(email, password):
        flash("Login successful!")
    else:
        flash("Invalid email or password.")
    return redirect(url_for('index'))

if __name__ == '__main__':
    create_users_table()
    app.run(debug=True)

