import pandas as pd
import sqlite3

database = "../nittanybusiness.db"
table = "Orders"
csv = "NittanyBusinessDataset_v3/Orders.csv"

df = pd.read_csv(csv)
conn = sqlite3.connect(database)
cursor = conn.cursor()

for _, row in df.iterrows():
    cursor.execute(f" INSERT INTO {table} (order_id, seller_email, listing_id, buyer_email, date, quantity, payment) VALUES (?, ?, ?, ?, ?, ?, ?)", (row['Order_ID'], row['Seller_Email'], row['Listing_ID'], row['Buyer_Email'], row['Date'], row['Quantity'], row['Payment']))

conn.commit()
conn.close()
