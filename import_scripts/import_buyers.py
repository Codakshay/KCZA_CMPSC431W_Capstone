import pandas as pd
import sqlite3

database = "../nittanybusiness.db"
table = "Buyers"
csv = "NittanyBusinessDataset_v3/Buyers.csv"

df = pd.read_csv(csv)
conn = sqlite3.connect(database)
cursor = conn.cursor()

for _, row in df.iterrows():
    cursor.execute(f" INSERT INTO {table} (email, business_name, buyer_address_id) VALUES (?, ?, ?)", (row['email'], row['business_name'], row['buyer_address_id']))

conn.commit()
conn.close()
