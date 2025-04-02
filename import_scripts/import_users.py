import pandas as pd
import sqlite3
import hashlib

database = "../nittanybusiness.db"
table = "Users"
csv = "NittanyBusinessDataset_v3/Users.csv"

# hashes the password
def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

df = pd.read_csv(csv)
df['hashed_password'] = df['password'].apply(hash_password) # applies the hash_password function to each element in the password column and creates a hashed_password column
df = df[['email', 'hashed_password']] # replaces the password column with the hashed_password column

conn = sqlite3.connect(database)
cursor = conn.cursor()

for _, row in df.iterrows(): # inserts the email and hashed_password for each row
    cursor.execute(f" INSERT INTO {table} (email, hashed_password) VALUES (?, ?)", (row['email'], row['hashed_password']))

conn.commit()
conn.close()
