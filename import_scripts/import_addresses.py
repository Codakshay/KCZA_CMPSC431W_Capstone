import pandas as pd
import sqlite3

database = "../nittanybusiness.db"
table = "Addresses"
csv = "NittanyBusinessDataset_v3/Address.csv"

df = pd.read_csv(csv)
conn = sqlite3.connect(database)
cursor = conn.cursor()

for _, row in df.iterrows():
    cursor.execute(f" INSERT INTO {table} (address_id, zipcode, street_num, street_name) VALUES (?, ?, ?, ?)", (row['address_id'], row['zipcode'], row['street_num'], row['street_name']))

conn.commit()
conn.close()
