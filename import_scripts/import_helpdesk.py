import pandas as pd
import sqlite3

database = "../nittanybusiness.db"
table = "Helpdesk"
csv = "NittanyBusinessDataset_v3/Helpdesk.csv"

df = pd.read_csv(csv)
conn = sqlite3.connect(database)
cursor = conn.cursor()

cursor.execute(f"DELETE FROM {table}")

for _, row in df.iterrows():
    cursor.execute(f" INSERT INTO {table} (email, position) VALUES (?, ?)", (row['email'], row['Position']))

conn.commit()
conn.close()
