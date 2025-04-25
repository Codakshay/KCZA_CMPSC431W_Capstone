import pandas as pd
import sqlite3

database = "../nittanybusiness.db"
table = "ZipcodeInfo"
csv = "NittanyBusinessDataset_v3/Zipcode_Info.csv"

df = pd.read_csv(csv)
conn = sqlite3.connect(database)
cursor = conn.cursor()

cursor.execute(f"DELETE FROM {table}")

for _, row in df.iterrows():
    cursor.execute(f" INSERT INTO {table} (zipcode, city, state) VALUES (?, ?, ?)", (row['zipcode'], row['city'], row['state']))

conn.commit()
conn.close()
