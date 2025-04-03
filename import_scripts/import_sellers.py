import pandas as pd
import sqlite3

database = "../nittanybusiness.db"
table = "Sellers"
csv = "NittanyBusinessDataset_v3/Sellers.csv"

df = pd.read_csv(csv)
conn = sqlite3.connect(database)
cursor = conn.cursor()

for _, row in df.iterrows():
    cursor.execute(f" INSERT INTO {table} (email, business_name, business_address_id, bank_routing_number, bank_account_number, balance) VALUES (?, ?, ?, ?, ?, ?)", (row['email'], row['business_name'], row['Business_Address_ID'], row['bank_routing_number'], row['bank_account_number'], row['balance']))

conn.commit()
conn.close()
