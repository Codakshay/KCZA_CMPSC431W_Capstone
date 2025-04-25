import pandas as pd
import sqlite3

database = "../nittanybusiness.db"
table = "Reviews"
csv = "NittanyBusinessDataset_v3/Reviews.csv"

df = pd.read_csv(csv)
conn = sqlite3.connect(database)
cursor = conn.cursor()

cursor.execute(f"DELETE FROM {table}")

for _, row in df.iterrows():
    cursor.execute(f" INSERT INTO {table} (order_id, rate, review_desc) VALUES (?, ?, ?)", (row['Order_ID'], row['Rate'], row[' Review_Desc']))

conn.commit()
conn.close()
