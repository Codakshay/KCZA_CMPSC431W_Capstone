import pandas as pd
import sqlite3
import hashlib

database = "nittanybusiness.db"
table = "Users"
csv = "Users.csv"

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

df = pd.read_csv(csv)
df['hashed_password'] = df['password'].apply(hash_password)
df = df[['email', 'hashed_password']]

conn = sqlite3.connect(database)
cursor = conn.cursor()

for _, row in df.iterrows():
    cursor.execute(f" INSERT INTO {table} (email, hashed_password) VALUES (?, ?)", (row['email'], row['hashed_password']))

conn.commit()
conn.close()
