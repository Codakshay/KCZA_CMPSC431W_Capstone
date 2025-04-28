from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import hashlib
import random
import string
from datetime import datetime
import search as s

app = Flask(__name__)
app.secret_key = "secret_key" # needed for flash messages
DATABASE = 'nittanybusiness.db'

# hashes the password
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def register_user_multi_roles(email: str, password: str, business_name: str, address_id: str, bank_routing_number: str, bank_account_number: str, roles: list) -> bool:
    hashed_pwd = hash_password(password)
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO users (email, hashed_password) VALUES (?, ?)", (email, hashed_pwd))
    except sqlite3.IntegrityError:
        # User exists, continue adding roles if needed
        pass

    try:                  
        for role in roles:
            if role == 'Buyer':
                cursor.execute("INSERT INTO buyers (email, business_name, buyer_address_id) VALUES (?,?,?)", (email, business_name, address_id))
            elif role == 'Seller':
                cursor.execute("INSERT INTO sellers (email, business_name, business_address_id, bank_routing_number, bank_account_number, balance) VALUES (?,?,?,?,?,?)", (email, business_name, address_id, bank_routing_number, bank_account_number, 0))
            else:
                continue  # Ignore unknown roles
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error:
        conn.close()
        return False

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


def get_user_role(email: str) -> list:
    """Return a list of roles assigned to the user."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    roles = []

    cursor.execute("SELECT 1 FROM buyers WHERE email = ?", (email,))
    if cursor.fetchone():
        roles.append("Buyer")

    cursor.execute("SELECT 1 FROM sellers WHERE email = ?", (email,))
    if cursor.fetchone():
        roles.append("Seller")

    cursor.execute("SELECT 1 FROM helpdesk WHERE email = ?", (email,))
    if cursor.fetchone():
        roles.append("HelpDesk")

    conn.close()
    return roles


def is_helpdesk() -> bool:
    return 'email' in session and 'HelpDesk' in get_user_role(session['email'])



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
    if 'email' in session:
        roles = get_user_role(session['email'])
        if "Seller" in roles:
            return redirect(url_for('seller_dashboard'))
        elif "Buyer" in roles:
            return redirect(url_for('buyer_dashboard'))
        elif "HelpDesk" in roles:
            return redirect(url_for('helpdesk_dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    email = request.form.get('email')
    password = request.form.get('password')
    roles = request.form.getlist('roles')  # allows selecting multiple roles
    business_name = request.form.get('business_name')
    street_num = request.form.get('street_num')
    street_name = request.form.get('street_name')
    zipcode = request.form.get('zipcode')
    bank_routing_number = request.form.get('bank_routing_number')
    bank_account_number = request.form.get('bank_account_number')

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # check for valid zipcode
    cursor.execute("SELECT zipcode FROM ZipcodeInfo WHERE zipcode = ?", (zipcode,))
    if not cursor.fetchone():
        flash("Invalid Zipcode")
        conn.close()
        return redirect(url_for('index'))

    # add address
    address_id = ""
    # create a new random id that matches the format of the given ids
    while True:
        address_id = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
        cursor.execute("SELECT * FROM Addresses WHERE address_id = ?", (address_id,))
        if not cursor.fetchone():
            break
    cursor.execute("INSERT INTO Addresses (address_id, zipcode, street_num, street_name) VALUES (?,?,?,?)", (address_id,zipcode,street_num,street_name))
    conn.commit()

    conn.close()

    if 'HelpDesk' in roles:
        flash("HelpDesk registration is restricted.")
        return redirect(url_for('index'))

    success = register_user_multi_roles(email, password, business_name, address_id, bank_routing_number, bank_account_number, roles)
    if success:
        session['email'] = email  # Automatically log in the user
        session['business_name'] = business_name
        flash(f"Registration successful as {', '.join(roles)}.")
    else:
        flash("Registration failed. Email might already exist.")
    return redirect(url_for('index'))

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

def get_business_name(email):
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.execute("SELECT business_name FROM Buyers WHERE email = ?", (email,))
    result = cursor.fetchone()
    if not result:
        cursor = conn.execute("SELECT business_name FROM Sellers WHERE email = ?", (email,))
        result = cursor.fetchone()
    conn.close()
    return result['business_name'] if result else "Unknown Seller"

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')

    if authenticate_user(email, password):
        session['email'] = email
        session['business_name'] = get_business_name(email)
        flash("Login successful!")
    else:
        flash("Invalid email or password.")
    return redirect(url_for('index'))



@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully.")
    return redirect(url_for('index'))

@app.route('/search', methods=["GET", "POST"])
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
        cursor.execute(
            "SELECT Listings.Seller_Email, Listings.Listing_ID, Listings.Product_Name, Listings.Product_Price, Sellers.business_name FROM Listings, Sellers WHERE Listings.Category = ? AND Listings.Status = 1 AND Listings.seller_email = Sellers.email", (query_category,))
        products = cursor.fetchall()

    
    if parent_category.endswith("- Promoted"):
        print(query_category.removesuffix(" - Promoted"))
        cursor.execute(
            """SELECT Listings.Listing_ID, Sellers.business_name
                FROM Listings, Sellers
                WHERE Listings.Product_Title = ? AND Listings.seller_email = Sellers.email
            """, (query_category.removesuffix(" - Promoted"),))
        products = cursor.fetchone()
        return redirect(url_for('show_product', seller_name=products[1],product_id=products[0]))
    
    conn.close()

    user_role = None
    if 'email' in session:
        user_role = get_user_role(session['email'])

    return render_template("categories.html",
                           parent_category=display_category,
                           subcategories=subcategories,
                           products=products,
                           user_role=user_role)


@app.route('/seller/add_listing', methods=["GET", "POST"])
def add_listing():
    if "email" not in session:
        flash("Please log in as a seller.")
        return redirect(url_for("index"))
    email = session["email"]
    role = get_user_role(email)
    if "Seller" not in role:
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
       flash("Please log in.")
       return redirect(url_for("index"))


   email = session["email"]
   roles = get_user_role(email)
   if 'Seller' not in roles:
       flash("Access restricted: Seller role required.")
       return redirect(url_for("index"))


   conn = sqlite3.connect(DATABASE)
   cursor = conn.cursor()
   cursor.execute("""
       SELECT listing_id, product_title, category, quantity, product_price
       FROM Listings
       WHERE seller_email = ? AND status = 1
   """, (email,))

   listings = cursor.fetchall()
   conn.close()


   return render_template("seller_dashboard.html", listings=listings, roles=roles)



@app.route('/buyer/dashboard')
def buyer_dashboard():
   if "email" not in session:
       flash("Please log in.")
       return redirect(url_for("index"))


   email = session["email"]
   roles = get_user_role(email)
   if 'Buyer' not in roles:
       flash("Access restricted: Buyer role required.")
       return redirect(url_for("index"))


   # Query orders from the database
   conn = sqlite3.connect('nittanybusiness.db')
   cursor = conn.cursor()
   cursor.execute('''
       SELECT Order_ID, Seller_Email, Listing_ID, Date, Quantity, Payment
       FROM Orders
       WHERE Buyer_Email = ?
   ''', (email,))
   orders = cursor.fetchall()
   conn.close()


   return render_template("buyer_dashboard.html", orders=orders, roles=roles)


@app.route('/support_request', methods=['GET', 'POST'])
def support_request():
    if 'email' not in session:
        flash("Please log in to submit a support request.")
        return redirect(url_for('index'))

    if request.method == 'POST':
        email         = session['email']
        req_type      = request.form.get('request_type', 'AddCategory').strip()
        description   = request.form.get('description', '').strip()

        with sqlite3.connect(DATABASE) as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO requests (sender_email, request_type, request_desc, request_status)
                VALUES (?, ?, ?, 0)
            """, (email, req_type, description))
            conn.commit()

        flash("Support request submitted to HelpDesk.")
        return redirect(url_for('profile'))

    return render_template('support_request.html')


def get_business_email(name):
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor = conn.execute("SELECT email FROM Sellers WHERE business_name = ?", (name,))
    result = cursor.fetchone()
    conn.close()
    return result['email'] if result else "Unknown Seller"


@app.route('/product/<string:seller_name>/<int:product_id>')
def show_product(seller_name, product_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Fetch product info
    cursor.execute("""
        SELECT 
            Listings.product_name, 
            Listings.product_price, 
            Listings.seller_email, 
            Listings.Product_Description,
            Listings.status, 
            Listings.quantity
        FROM Listings
        WHERE Listings.listing_id = ?
    """, (product_id,))
    row = cursor.fetchone()

    if row:
        seller_email = row[2]

        # Fetch seller's average rating
        cursor.execute("""
            SELECT AVG(Rate) 
            FROM Reviews
            INNER JOIN Orders ON Reviews.Order_ID = Orders.Order_ID
            WHERE Orders.seller_email = ?
        """, (seller_email,))
        rating_row = cursor.fetchone()
        seller_rating = round(rating_row[0], 2) if rating_row and rating_row[0] is not None else None

        # Build product dictionary
        product = {
            'name': row[0],
            'price': row[1],
            'seller_email': seller_email,
            'description': row[3],
            'status': row[4],
            'quantity': row[5],
            'business_name': seller_name,
            'seller_rating': seller_rating
        }

        #  Fetch product reviews
        cursor.execute("""
            SELECT Reviews.Rate, Reviews.Review_Desc
            FROM Reviews
            INNER JOIN Orders ON Reviews.Order_ID = Orders.Order_ID
            WHERE Orders.Listing_ID = ?
        """, (product_id,))
        review_rows = cursor.fetchall()

        reviews = [{'rating': r[0], 'description': r[1]} for r in review_rows]

        conn.close()

        return render_template('product.html', product=product, product_id=product_id, reviews=reviews)

    else:
        conn.close()
        return "Product not found", 404


def generate_order_id():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(Order_ID) FROM Orders ")
    result = cursor.fetchone()[0]
    conn.close()
    return 1 if result is None else result + 1


@app.route('/order/<int:product_id>', methods=['GET', 'POST'])
def order_product(product_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Get product info
    cursor.execute("""
    SELECT 
        Listings.product_name, 
        Listings.product_price, 
        Listings.seller_email, 
        Listings.Product_Description,
        Listings.status, 
        Listings.quantity,
        Sellers.business_name,
        Listings.Listing_ID
    FROM Listings
    JOIN Sellers ON Listings.seller_email = Sellers.email
    WHERE Listings.listing_id = ?
""", (product_id,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        return "Product not found", 404

    seller_email = row[2]

    # Fetch seller's average rating
    cursor.execute("""
        SELECT AVG(Rate) FROM Reviews
        INNER JOIN Orders ON Reviews.order_id = Orders.order_id
        WHERE Orders.seller_email = ?
    """, (seller_email,))
    rating_row = cursor.fetchone()
    seller_rating = round(rating_row[0], 2) if rating_row and rating_row[0] is not None else None

    product = {
        'name': row[0],
        'price': row[1],
        'seller_email': row[2],
        'description': row[3],
        'status': row[4],
        'quantity': row[5],
        'business_name': row[6],
        'listing_id': row[7],
        'seller_rating': seller_rating
    }

    # Get current buyer's email from session
    buyer_email = session.get('email')
    if not buyer_email:
        conn.close()
        return "User not logged in", 403

    # Get list of credit cards owned by the buyer
    cursor.execute("SELECT owner_email, credit_card_num FROM CreditCards WHERE owner_email = ?", (buyer_email,))
    cards = cursor.fetchall()
    credit_cards = [{'id': c[0], 'credit_card_num': c[1]} for c in cards]

    if request.method == 'POST':
        if 'add_card' in request.form:
            # Fetch and clean new card data
            new_card = request.form.get('new_credit_card', '').strip()
            card_type = request.form.get('card_type', '').strip()
            expire_month = request.form.get('expire_month', '').strip()
            expire_year = request.form.get('expire_year', '').strip()
            security_code = request.form.get('security_code', '').strip()

            formatted_card = '-'.join(new_card[i:i+4] for i in range(0, 16, 4))
            # Check if card already exists
            cursor.execute("SELECT 1 FROM CreditCards WHERE credit_card_num = ?", (formatted_card,))
            existing_card = cursor.fetchone()

            try:
                # Insert into CreditCards table
                cursor.execute("""
                    INSERT INTO CreditCards (credit_card_num, card_type, expire_month, expire_year, security_code, owner_email)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (formatted_card, card_type, expire_month, expire_year, security_code, buyer_email))
                conn.commit()
            except:
                return "Credit card already exists", 400

            # Refresh credit cards after insert
            cursor.execute("SELECT rowid, credit_card_num FROM CreditCards WHERE owner_email = ?", (buyer_email,))
            cards = cursor.fetchall()
            credit_cards = [{'id': c[0], 'credit_card_num': c[1]} for c in cards]

        elif 'purchase' in request.form:
            quantity_to_purchase = int(request.form.get('quantity', 0))

            if quantity_to_purchase > product['quantity']:
                conn.close()
                return f"Not enough inventory. Only {product['quantity']} left.", 400

            new_quantity = product['quantity'] - quantity_to_purchase
            cursor.execute("UPDATE Listings SET quantity = ? WHERE listing_id = ?", (new_quantity, product_id))

            if new_quantity == 0:
                cursor.execute("UPDATE Listings SET status = 2 WHERE listing_id = ?", (product_id,))

            total_sale_amount = product['price'] * quantity_to_purchase

            # check if product is promoted
            cursor.execute("SELECT category_name FROM Categories WHERE category_name = ?", (product['name'],))
            if cursor.fetchone() is not None:
                total_sale_amount *= .95

            cursor.execute("""
                UPDATE Sellers 
                SET balance = balance + ? 
                WHERE email = ?
            """, (total_sale_amount, product['seller_email']))

            order_id= generate_order_id()

            cursor.execute("""
                INSERT INTO Orders (order_id, seller_email, listing_id, buyer_email, date, quantity, payment)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (order_id, product['seller_email'], product['listing_id'], buyer_email, datetime.now().strftime("%Y/%m/%d"),quantity_to_purchase,total_sale_amount))
            
            conn.commit()
            conn.close()

            return redirect(url_for('review_product', product_id=product_id, quantity=quantity_to_purchase, order_id=order_id))
        



    quantity = request.args.get('quantity', type=int)
    conn.close()
    return render_template('order_product.html',
                           product=product,
                           product_id=product_id,
                           quantity=quantity,
                           credit_cards=credit_cards)


@app.route('/edit_listing/<int:listing_id>', methods=['GET', 'POST'])
def edit_listing(listing_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    if request.method == 'POST':
        title = request.form['title']
        category = request.form['category']
        quantity = request.form['quantity']
        price = request.form['price']
        promote = request.form.get('promote')

        cursor.execute("""
            UPDATE Listings
            SET product_title = ?, category = ?, quantity = ?, product_price = ?
            WHERE listing_id = ?
        """, (title, category, quantity, price, listing_id))

        if promote == '1':
            cursor.execute("""
                INSERT INTO Categories (parent_category, category_name)
                SELECT 'Root', ?
                WHERE NOT EXISTS (
                    SELECT 1 FROM Categories WHERE parent_category = 'Root' AND category_name = ?
                )
            """, (title + " - Promoted", title + " - Promoted"))
        else:
            cursor.execute("""
                DELETE FROM Categories
                WHERE parent_category = 'Root' AND category_name = ?
            """, (title + " - Promoted",))


        conn.commit()
        conn.close()

        flash('Listing updated successfully.')
        return redirect(url_for('seller_dashboard'))

    else:
        cursor.execute("""
            SELECT product_title, category, quantity, product_price
            FROM Listings
            WHERE listing_id = ?
        """, (listing_id,))
        listing = cursor.fetchone()

        cursor.execute("""
            SELECT parent_category, category_name
            FROM Categories
            WHERE Categories.category_name = ?
        """, (listing[0]+" - Promoted",))


        # add info on if it is already promoted
        listing_info = list(listing)
        category_heirarchy = cursor.fetchone()
        if category_heirarchy is not None and category_heirarchy[0] == "Root":
            listing_info.append(True)
        else:
            listing_info.append(False)
        conn.close()

        if listing_info:
            return render_template('edit_listing.html', listing_id=listing_id, listing=listing_info)
        else:
            return "Listing not found.", 404



@app.route('/delete_listing/<int:listing_id>', methods=['POST'])
def delete_listing(listing_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Set status to 0 (inactive) instead of deleting
    cursor.execute("""
        UPDATE Listings
        SET status = 0
        WHERE listing_id = ?
    """, (listing_id,))
    conn.commit()
    conn.close()

    flash('Listing has been marked as inactive.')
    return redirect(url_for('seller_dashboard'))



@app.route('/review/<int:product_id>', methods=['GET', 'POST'])
def review_product(product_id):
    quantity = request.args.get('quantity', type=int)
    order_id = request.args.get('order_id', type=int)
    buyer_email = session.get('email')
    if not buyer_email:
        return "User not logged in", 403

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    if request.method == 'POST':
        # Get rating and detailed review
        rating = request.form.get('rating')
        review_desc = request.form.get('review_desc')

        # Insert into Reviews table
        cursor.execute("""
            INSERT INTO Reviews (order_id, rate, review_desc)
            VALUES (?, ?, ?)
        """, (order_id, rating, review_desc))

        conn.commit()
        conn.close()

        return redirect(url_for('search')) 


    cursor.execute("""
    SELECT 
        Listings.product_name, 
        Sellers.business_name,
        Listings.Listing_ID
    FROM Listings
    JOIN Sellers ON Listings.seller_email = Sellers.email
    WHERE Listings.listing_id = ?
""", (product_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return "Product not found", 404

    product = {
        'name': row[0],
        'business_name': row[1]
    }

    return render_template('review_product.html', product=product, quantity=quantity)




@app.route('/helpdesk/dashboard')
def helpdesk_dashboard():
    if not is_helpdesk():
        flash("HelpDesk access required.")
        return redirect(url_for('index'))

    email = session['email']
    conn  = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cur   = conn.cursor()

    # Unassigned requests (status = 0)
    cur.execute("""
        SELECT * FROM requests
        WHERE request_type = 'AddCategory'
          AND request_status = 0
        ORDER BY request_id
    """)
    unassigned = cur.fetchall()

    # Claimed/Completed requests (filter from session)
    my_claimed = session.get('claimed_requests', [])

    my_requests = []
    if my_claimed:
        format_strings = ','.join(['?'] * len(my_claimed))
        cur.execute(f"""
            SELECT * FROM requests
            WHERE request_id IN ({format_strings})
            ORDER BY request_status, request_id
        """, tuple(my_claimed))
        my_requests = cur.fetchall()

    conn.close()

    return render_template('helpdesk_dashboard.html',
                           unassigned=unassigned,
                           my_requests=my_requests)


@app.route('/helpdesk/claim/<int:req_id>', methods=['POST'])
def claim_request(req_id):
    if not is_helpdesk():
        return redirect(url_for('index'))

    # Save claim into session
    claimed = session.get('claimed_requests', [])
    if req_id not in claimed:
        claimed.append(req_id)
    session['claimed_requests'] = claimed

    # Update database: mark request_status = 1 (in-progress)
    with sqlite3.connect(DATABASE) as conn:
        cur = conn.cursor()
        cur.execute("""
            UPDATE requests
            SET request_status = 1
            WHERE request_id = ? AND request_status = 0
        """, (req_id,))
        conn.commit()

    flash("Request claimed.")
    return redirect(url_for('helpdesk_dashboard'))


@app.route('/helpdesk/complete/<int:req_id>', methods=['POST'])
def complete_request(req_id):
    if not is_helpdesk():
        return redirect(url_for('index'))

    claimed = session.get('claimed_requests', [])
    if req_id not in claimed:
        flash("You must claim this request first.")
        return redirect(url_for('helpdesk_dashboard'))

    with sqlite3.connect(DATABASE) as conn:
        cur = conn.cursor()
        # Get description to extract category
        cur.execute("""
            SELECT request_desc FROM requests
            WHERE request_id = ?
        """, (req_id,))
        row = cur.fetchone()
        if not row:
            flash("Request not found.")
            return redirect(url_for('helpdesk_dashboard'))

        desc = row[0]
        new_cat = desc.strip().split()[-1]  # naive extraction

        # Add category if missing
        cur.execute("SELECT 1 FROM Categories WHERE category_name = ?", (new_cat,))
        if not cur.fetchone():
            cur.execute("""
                INSERT INTO Categories (category_name, parent_category)
                VALUES (?, 'Root')
            """, (new_cat,))

        # Mark request as completed
        cur.execute("""
            UPDATE requests
            SET request_status = 2
            WHERE request_id = ?
        """, (req_id,))
        conn.commit()

    flash(f"Category '{new_cat}' added and request marked complete.")
    return redirect(url_for('helpdesk_dashboard'))



if __name__ == '__main__':
    # create_users_table()
    app.run(debug=True)
