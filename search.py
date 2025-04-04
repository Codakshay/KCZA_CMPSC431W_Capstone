import sqlite3

DATABASE = 'nittanybusiness.db'

def get_matching_sellers(keywords):
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    keyword_pattern = f"%{keywords}%"
    cursor = conn.execute("SELECT email FROM Sellers WHERE business_name LIKE ?", (keyword_pattern,))
    matching_sellers = [row['email'] for row in cursor.fetchall()]
    conn.close()
    return matching_sellers

def get_business_name(email):
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.execute("SELECT business_name FROM Sellers WHERE email = ?", (email,))
    result = cursor.fetchone()
    conn.close()
    return result['business_name'] if result else "Unknown Seller"

def search_for(keywords, min_price, max_price):
    if not keywords:
        return None

    query = """
        SELECT product_name, product_price, seller_email, status
        FROM Listings
        WHERE (status = 1 OR status = 2)
    """
    params = []

    query += """
        AND (product_title LIKE ?
        OR product_description LIKE ?
        OR category LIKE ?)
    """
    keyword_pattern = f"%{keywords}%"
    params.extend([keyword_pattern] * 3)

    matching_seller_emails = get_matching_sellers(keywords)

    if min_price is not None:
        query += " AND product_price >= ?"
        params.append(min_price)

    if max_price is not None:
        query += " AND product_price <= ?"
        params.append(max_price)

    if len(matching_seller_emails) > 0:
        query += f" OR seller_email IN ({", ".join(["?"] * len(matching_seller_emails))})"
        params.extend(matching_seller_emails)

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.execute(query, params)
    results = cursor.fetchall()
    conn.close()

    products = []
    for row in results:
        product = dict(row)
        product['business_name'] = get_business_name(product['seller_email'])
        products.append(product)

    return products
