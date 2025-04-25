import pandas as pd
import sqlite3

database = "../nittanybusiness.db"
table = "CreditCards"
csv = "NittanyBusinessDataset_v3/Credit_Cards.csv"

df = pd.read_csv(csv)
conn = sqlite3.connect(database)
cursor = conn.cursor()

cursor.execute(f"DELETE FROM {table}")

for _, row in df.iterrows():
    cursor.execute(f" INSERT INTO {table} (credit_card_num, card_type, expire_month, expire_year, security_code, owner_email) VALUES (?, ?, ?, ?, ?, ?)", (row['credit_card_num'], row['card_type'], row['expire_month'], row['expire_year'], row['security_code'], row['Owner_email']))

conn.commit()
conn.close()
