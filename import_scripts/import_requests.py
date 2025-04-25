import pandas as pd
import sqlite3

database = "../nittanybusiness.db"
table = "Requests"
csv = "NittanyBusinessDataset_v3/Requests.csv"

df = pd.read_csv(csv)
conn = sqlite3.connect(database)
cursor = conn.cursor()

cursor.execute(f"DELETE FROM {table}")

for _, row in df.iterrows():
    cursor.execute(f" INSERT INTO {table} (request_id, sender_email, helpdesk_staff_email, request_type, request_desc, request_status) VALUES (?, ?, ?, ?, ?, ?)", (row['request_id'], row['sender_email'], row['helpdesk_staff_email'], row['request_type'], row['request_desc'], row['request_status']))

conn.commit()
conn.close()
