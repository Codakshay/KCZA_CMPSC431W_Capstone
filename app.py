from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import hashlib

import search as s

app = Flask(__name__)
app.secret_key = "secret_key" # needed for flash messages
DATABASE = 'nittanybusiness.db'

# hashes the password
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

# creates the Users table
# def create_users_table():
#     conn = sqlite3.connect(DATABASE)
#     cursor = conn.cursor()
#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS Users (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             email TEXT UNIQUE NOT NULL,
#             hashed_password TEXT NOT NULL
#         )
#     ''')
#     conn.commit()
#     conn.close()

# inserts a new user into the User table, returns true on success
def register_user(email: str, password: str) -> bool:
    hashed_pwd = hash_password(password)
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO Users (email, hashed_password) VALUES (?, ?)", (email, hashed_pwd))
        conn.commit()
        return True
    except sqlite3.IntegrityError: # Email already exists
        return False
    finally:
        conn.close()

# makes sure the users email and password are correct and in the Users table
def authenticate_user(email: str, password: str) -> bool:
    hashed_input = hash_password(password)
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT hashed_password FROM Users WHERE email = ?", (email,))
    result = cursor.fetchone()
    conn.close()
    if result is None: # not in the table
        return False
    stored_hash = result[0]
    return stored_hash == hashed_input # if true, password match

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
    return redirect(url_for('index')) # redirect prevents sending the form data again

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    if authenticate_user(email, password):
        flash("Login successful!")
    else:
        flash("Invalid email or password.")
    return redirect(url_for('index')) # redirect prevents sending the form data again

@app.route('/search', methods=["GET"])
def search():
    keywords = request.args.get('keywords', '').strip()
    min_price = request.args.get('min_price', type=int)
    max_price = request.args.get('max_price', type=int)
    products = s.search_for(keywords, min_price, max_price)
    return render_template("search.html", results=products)

if __name__ == '__main__':
    # create_users_table()
    app.run(debug=True)
