"""
Import cleaned transaction data from CSV to SQLite database.

This script:
1. Reads the cleaned CSV file
2. Creates SQLite transactions table with proper schema
3. Inserts all records
4. Verifies data integrity
"""

import pandas as pd
import sqlite3
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

DB_PATH = 'ecommerce.db'
CSV_PATH = 'data/sample_transactions.csv'


def import_csv_to_db():
    """Import CSV data into SQLite database."""
    
    try:
        logger.info("="*80)
        logger.info("IMPORTING CSV DATA TO SQLite DATABASE")
        logger.info("="*80)
        
        # Step 1: Read CSV
        logger.info(f"\n[STEP 1] Reading CSV from {CSV_PATH}...")
        df = pd.read_csv(CSV_PATH)
        logger.info(f"✓ Loaded {len(df)} records")
        logger.info(f"✓ Columns: {list(df.columns)}")
        
        # Step 2: Connect to database
        logger.info(f"\n[STEP 2] Connecting to SQLite database at {DB_PATH}...")
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        logger.info("✓ Connected to database")
        
        # Step 3: Drop old table if exists
        logger.info("\n[STEP 3] Preparing database table...")
        cursor.execute('DROP TABLE IF EXISTS transactions')
        logger.info("✓ Dropped old transactions table (if exists)")
        
        # Step 4: Create transactions table with proper schema
        logger.info("\n[STEP 4] Creating transactions table...")
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
        logger.info("✓ Created transactions table")
        
        # Step 5: Insert data
        logger.info("\n[STEP 5] Inserting data into database...")
        inserted = 0
        failed = 0
        
        for idx, row in df.iterrows():
            try:
                cursor.execute('''
                    INSERT INTO transactions 
                    (transaction_id, user_name, country, product_category, 
                     purchase_amount, payment_method, transaction_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    str(row['transaction_id']),
                    str(row['user_name']),
                    str(row['country']),
                    str(row['product_category']),
                    float(row['purchase_amount']),
                    str(row['payment_method']),
                    str(row['transaction_date'])
                ))
                inserted += 1
            except Exception as e:
                failed += 1
                if failed <= 5:  # Log first 5 errors only
                    logger.warning(f"  ⚠️ Row {idx} failed: {e}")
        
        conn.commit()
        logger.info(f"✓ Inserted {inserted} records, {failed} failed")
        
        # Step 6: Verify import
        logger.info("\n[STEP 6] Verifying data...")
        cursor.execute('SELECT COUNT(*) FROM transactions')
        count = cursor.fetchone()[0]
        logger.info(f"✓ Total records in database: {count}")
        
        # Step 7: Display sample data
        logger.info("\n[STEP 7] Sample data from database:")
        cursor.execute('SELECT * FROM transactions LIMIT 10')
        rows = cursor.fetchall()
        for i, row in enumerate(rows, 1):
            logger.info(f"  {i}. ID={row[1]}, User={row[2]}, Amount=${row[5]:.2f}, Date={row[7]}")
        
        # Step 8: Get statistics
        logger.info("\n[STEP 8] Database statistics:")
        cursor.execute('SELECT COUNT(DISTINCT user_name) FROM transactions')
        unique_users = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(DISTINCT country) FROM transactions')
        unique_countries = cursor.fetchone()[0]
        cursor.execute('SELECT SUM(purchase_amount) FROM transactions')
        total_revenue = cursor.fetchone()[0]
        cursor.execute('SELECT AVG(purchase_amount) FROM transactions')
        avg_amount = cursor.fetchone()[0]
        
        logger.info(f"  - Unique Users: {unique_users}")
        logger.info(f"  - Unique Countries: {unique_countries}")
        logger.info(f"  - Total Revenue: ${total_revenue:.2f}")
        logger.info(f"  - Average Transaction: ${avg_amount:.2f}")
        
        conn.close()
        
        logger.info("\n" + "="*80)
        logger.info("✅ DATABASE IMPORT COMPLETED SUCCESSFULLY")
        logger.info("="*80)
        logger.info("\n✅ You can now run: python -m uvicorn app.main:app --reload\n")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error during import: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = import_csv_to_db()
    exit(0 if success else 1)