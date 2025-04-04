import pandas as pd
import sqlite3

database = "../nittanybusiness.db"
table = "Listings"
csv = "NittanyBusinessDataset_v3/Product_Listings.csv"

def remove_dollar_sign(price):
    return price.replace("$", "")

df = pd.read_csv(csv)
df['Product_Price'] = df['Product_Price'].apply(remove_dollar_sign)

conn = sqlite3.connect(database)
cursor = conn.cursor()

for _, row in df.iterrows():
    cursor.execute(f" INSERT INTO {table} (seller_email, listing_id, category, product_title, product_name, product_description, quantity, product_price, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (row['Seller_Email'], row['Listing_ID'], row['Category'], row['Product_Title'], row['Product_Name'], row['Product_Description'], row['Quantity'], row['Product_Price'], row['Status']))

conn.commit()
conn.close()
