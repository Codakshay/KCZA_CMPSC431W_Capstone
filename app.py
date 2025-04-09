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
def register_user(email: str, password: str, role: str) -> bool:
    """Register a new user and assign a role in a separate table."""
    if role == 'HelpDesk':
        return False  # Block public HelpDesk registration

    hashed_pwd = hash_password(password)
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO users (email, hashed_password) VALUES (?, ?)", (email, hashed_pwd))

        if role == 'Buyer':
            cursor.execute("INSERT INTO buyers (email) VALUES (?)", (email,))
        elif role == 'Seller':
            cursor.execute("INSERT INTO sellers (email) VALUES (?)", (email,))
        else:
            return False  # Unknown role

        conn.commit()
        return True

    except sqlite3.IntegrityError:
        return False  # Email already exists
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

def submit_email_change_request(current_email: str, new_email: str) -> bool:
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    try:
        # Check if a pending request already exists
        cursor.execute('''
            SELECT * FROM requests
            WHERE sender_email = ? AND request_type = 'ChangeID' AND request_status = 0
        ''', (current_email,))
        if cursor.fetchone():
            return False  # Request already pending

        # Insert the new request
        request_desc = f"Please change my ID to {new_email}"
        cursor.execute('''
            INSERT INTO requests (sender_email, request_type, request_desc, request_status)
            VALUES (?, 'ChangeID', ?, 0)
        ''', (current_email, request_desc))
        conn.commit()
        return True

    except sqlite3.Error:
        return False
    finally:
        conn.close()


def get_user_role(email: str) -> str:
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("SELECT 1 FROM buyers WHERE email = ?", (email,))
    if cursor.fetchone():
        return 'Buyer'

    cursor.execute("SELECT 1 FROM sellers WHERE email = ?", (email,))
    if cursor.fetchone():
        return 'Seller'

    cursor.execute("SELECT 1 FROM helpdesk WHERE email = ?", (email,))
    if cursor.fetchone():
        return 'HelpDesk'

    return 'Unknown'

def generate_listing_id(seller_email):
    """Generate a unique Listing_ID for the given seller."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(Listing_ID) FROM Listings WHERE Seller_Email = ?", (seller_email,))
    result = cursor.fetchone()[0]
    conn.close()
    return 1 if result is None else result + 1

@app.route('/')
def index():
    return render_template('index.html')



@app.route('/register', methods=['POST'])
def register():
    email = request.form.get('email')
    password = request.form.get('password')
    role = request.form.get('role')

    if register_user(email, password, role):
        flash(f"Registration successful as {role}. You can now log in.")
    else:
        flash("Registration failed. Email might already exist or HelpDesk access is restricted.")
    return redirect(url_for('index'))

from flask import session
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'email' not in session:
        flash("Please log in to access your profile.")
        return redirect(url_for('index'))

    email = session['email']

    if request.method == 'POST':
        new_password = request.form.get('password')

        if new_password:
            hashed_pwd = hash_password(new_password)
            conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET hashed_password = ? WHERE email = ?", (hashed_pwd, email))
            conn.commit()
            conn.close()
            flash("Password updated successfully.")

        return redirect(url_for('profile'))

    return render_template('profile.html', email=email)

@app.route('/request_email_change', methods=['GET', 'POST'])
def request_email_change():
    if 'email' not in session:
        flash("Please log in to request an email change.")
        return redirect(url_for('index'))

    current_email = session['email']

    if request.method == 'POST':
        new_email = request.form.get('new_email')

        if submit_email_change_request(current_email, new_email):
            flash("Email change request submitted successfully. Await HelpDesk approval.")
        else:
            flash("You already have a pending email change request.")

        return redirect(url_for('profile'))

    return render_template('request_email_change.html', current_email=current_email)

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')

    if authenticate_user(email, password):
        session['email'] = email
        role = get_user_role(email)

        flash(f"Login successful as {role}!")

        if role == 'Buyer':
            return redirect(url_for('search'))
        elif role == 'Seller':
            return redirect(url_for('profile'))  # or a dedicated seller page
        elif role == 'HelpDesk':
            return redirect(url_for('profile'))  # or a HelpDesk dashboard
        else:
            flash("Unknown role. Redirecting to profile.")
            return redirect(url_for('profile'))
    else:
        flash("Invalid email or password.")
        return redirect(url_for('index'))



@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully.")
    return redirect(url_for('index'))

@app.route('/search', methods=["GET"])
def search():
    keywords = request.args.get('keywords', '').strip()
    min_price = request.args.get('min_price', type=int)
    max_price = request.args.get('max_price', type=int)
    products = s.search_for(keywords, min_price, max_price)
    return render_template("search.html", results=products)

@app.route('/categories/<parent_category>')
def view_category(parent_category):
    if parent_category == "All":
        query_category = "Root"
        display_category = "All"
    else:
        query_category = parent_category
        display_category = parent_category

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT category_name FROM Categories WHERE parent_category = ?", (query_category,))
    subcategories = cursor.fetchall()

    products = []
    if query_category != "Root":
        cursor.execute("""
            SELECT Seller_Email, Listing_ID, Product_Title, Product_Price 
            FROM Listings 
            WHERE Category = ? AND Status = 1
        """, (query_category,))
        products = cursor.fetchall()
    conn.close()

    return render_template("categories.html", parent_category=display_category, subcategories=subcategories, products=products)

@app.route('/seller/add_listing', methods=["GET", "POST"])
def add_listing():
    if "email" not in session:
        flash("Please log in as a seller.")
        return redirect(url_for("index"))
    email = session["email"]
    role = get_user_role(email)
    if role != "Seller":
        flash("Access restricted: Only sellers can add listings.")
        return redirect(url_for("index"))

    if request.method == "POST":
        category = request.form.get("category")
        product_title = request.form.get("product_title")
        product_name = request.form.get("product_name")
        product_description = request.form.get("product_description")
        try:
            quantity = int(request.form.get("quantity"))
            product_price = float(request.form.get("product_price"))
        except (ValueError, TypeError):
            flash("Quantity and price must be numeric.")
            return redirect(url_for("add_listing"))
        listing_id = generate_listing_id(email)
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO Listings (Seller_Email, Listing_ID, Category, Product_Title, Product_Name, Product_Description, Quantity, Product_Price, Status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
            ''', (email, listing_id, category, product_title, product_name, product_description, quantity, product_price))
            conn.commit()
        flash("Product listing added successfully.")
        return redirect(url_for("seller_dashboard"))
    else:
        # For GET requests, load available categories to choose from.
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT category_name FROM Categories")
        categories = cursor.fetchall()
        conn.close()
        return render_template("add_listing.html", categories=categories)

@app.route('/seller/dashboard')
def seller_dashboard():
    if "email" not in session:
        flash("Please log in as a seller.")
        return redirect(url_for("index"))
    email = session["email"]
    role = get_user_role(email)
    if role != "Seller":
        flash("Access restricted: Only sellers can view the dashboard.")
        return redirect(url_for("index"))
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT Listing_ID, Product_Title, Category, Quantity, Product_Price, Status 
        FROM Listings 
        WHERE Seller_Email = ?
    """, (email,))
    listings = cursor.fetchall()
    conn.close()
    return render_template("seller_dashboard.html", listings=listings)

if __name__ == '__main__':
    # create_users_table()
    app.run(debug=True)
