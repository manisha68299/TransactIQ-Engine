import pandas as pd
import sqlite3
from datetime import datetime

# Read cleaned CSV
df = pd.read_csv('data/sample_transactions.csv')

# Connect to SQLite
conn = sqlite3.connect('ecommerce.db')
cursor = conn.cursor()

# Drop old table if exists
cursor.execute('DROP TABLE IF EXISTS transactions')

# Create transactions table
cursor.execute('''
    CREATE TABLE transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        transaction_id TEXT UNIQUE NOT NULL,
        user_name TEXT NOT NULL,
        country TEXT NOT NULL,
        product_category TEXT NOT NULL,
        purchase_amount REAL NOT NULL,
        payment_method TEXT NOT NULL,
        transaction_date TIMESTAMP NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

# Insert data
for _, row in df.iterrows():
    cursor.execute('''
        INSERT INTO transactions 
        (transaction_id, user_name, country, product_category, 
         purchase_amount, payment_method, transaction_date)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        row['transaction_id'],
        row['user_name'],
        row['country'],
        row['product_category'],
        row['purchase_amount'],
        row['payment_method'],
        row['transaction_date']
    ))

conn.commit()

# Verify import
cursor.execute('SELECT COUNT(*) FROM transactions')
count = cursor.fetchone()[0]
print(f"✅ Successfully imported {count} transactions to SQLite")

cursor.execute('SELECT * FROM transactions LIMIT 5')
print("\nSample data from database:")
for row in cursor.fetchall():
    print(row)

conn.close()