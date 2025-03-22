import sqlite3
import hashlib
import csv

def sha256_hash(password):
    """User-defined function that returns a SHA256 hash of the input password."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

# Connect to (or create) the SQLite database file (users.db)
conn = sqlite3.connect('users.db')

# Register the custom SHA256 function with SQLite under the name 'sha256'
conn.create_function("sha256", 1, sha256_hash)

cursor = conn.cursor()

# 1. Create a temporary table to load CSV data (plain-text passwords)
cursor.execute('''
CREATE TABLE IF NOT EXISTS temp_users (
    email TEXT,
    password TEXT
)
''')

# 2. Create the final users table to store hashed passwords
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL
)
''')

# 3. Read the CSV file and insert data into temp_users using 'utf-8-sig' encoding to remove BOM
with open('Users.csv', newline='', encoding='utf-8-sig') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        print("Row keys:", list(row.keys()))
        print("Row data:", row)
        cursor.execute("INSERT INTO temp_users (email, password) VALUES (?, ?)",
                       (row['email'], row['password']))

# 4. Insert data into the final users table by hashing the passwords using our custom 'sha256' function
cursor.execute('''
INSERT INTO users (email, hashed_password)
SELECT email, sha256(password)
FROM temp_users
''')

# 5. (Optional) Drop the temporary table as it's no longer needed
cursor.execute("DROP TABLE temp_users")

# Commit changes and close the connection
conn.commit()
conn.close()

print("Data imported and passwords hashed successfully.")
