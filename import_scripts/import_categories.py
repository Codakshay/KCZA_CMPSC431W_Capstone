import pandas as pd
import sqlite3

database = "../nittanybusiness.db"
table = "Categories"
csv = "NittanyBusinessDataset_v3/Categories.csv"

df = pd.read_csv(csv)
conn = sqlite3.connect(database)
cursor = conn.cursor()

cursor.execute(f"DELETE FROM {table}")

for _, row in df.iterrows():
    cursor.execute(f" INSERT INTO {table} (parent_category, category_name) VALUES (?, ?)", (row['parent_category'], row['category_name']))

conn.commit()
conn.close()
