"""
Import cleaned transaction data from CSV to SQLite database.

This script:
1. Reads cleaned CSV data
2. Creates SQLite transactions table
3. Inserts records into database
4. Verifies database integrity
5. Displays analytics summary
"""

import pandas as pd
import sqlite3
from pathlib import Path
import logging
import traceback

# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DB_PATH = BASE_DIR / "ecommerce.db"
CSV_PATH = BASE_DIR / "data" / "cleaned_transactions.csv"

# ============================================================
# LOGGING CONFIGURATION
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# ============================================================
# MAIN FUNCTION
# ============================================================

def import_csv_to_db():
    """
    Import cleaned CSV data into SQLite database.
    """

    try:

        logger.info("=" * 80)
        logger.info("IMPORTING CSV DATA TO SQLITE DATABASE")
        logger.info("=" * 80)

        # ====================================================
        # STEP 1: READ CSV
        # ====================================================

        logger.info(f"\n[STEP 1] Reading CSV from {CSV_PATH}")

        if not CSV_PATH.exists():
            logger.error(f"CSV file not found: {CSV_PATH}")
            return False

        df = pd.read_csv(CSV_PATH)

        logger.info(f"Loaded {len(df)} records")
        logger.info(f"Columns: {list(df.columns)}")

        # ====================================================
        # STEP 2: CONNECT TO DATABASE
        # ====================================================

        logger.info(f"\n[STEP 2] Connecting to SQLite database")

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        logger.info(f"Connected to database at {DB_PATH}")

        # ====================================================
        # STEP 3: DROP OLD TABLE
        # ====================================================

        logger.info("\n[STEP 3] Preparing database table")

        cursor.execute("DROP TABLE IF EXISTS transactions")

        logger.info("Old transactions table removed")

        # ====================================================
        # STEP 4: CREATE TABLE
        # ====================================================

        logger.info("\n[STEP 4] Creating transactions table")

        cursor.execute("""
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
        """)

        logger.info("Transactions table created successfully")

        # ====================================================
        # STEP 5: INSERT DATA
        # ====================================================

        logger.info("\n[STEP 5] Inserting data into database")

        inserted = 0
        failed = 0

        insert_query = """
            INSERT INTO transactions (
                transaction_id,
                user_name,
                country,
                product_category,
                purchase_amount,
                payment_method,
                transaction_date
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """

        for idx, row in df.iterrows():

            try:

                cursor.execute(insert_query, (
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

                if failed <= 5:
                    logger.warning(f"Row {idx} failed: {e}")

        conn.commit()

        logger.info(f"Inserted records: {inserted}")
        logger.info(f"Failed records: {failed}")

        # ====================================================
        # STEP 6: VERIFY DATA
        # ====================================================

        logger.info("\n[STEP 6] Verifying database records")

        cursor.execute("SELECT COUNT(*) FROM transactions")

        total_records = cursor.fetchone()[0]

        logger.info(f"Total records in database: {total_records}")

        # ====================================================
        # STEP 7: DISPLAY SAMPLE DATA
        # ====================================================

        logger.info("\n[STEP 7] Sample database records")

        cursor.execute("""
            SELECT
                transaction_id,
                user_name,
                purchase_amount,
                transaction_date
            FROM transactions
            LIMIT 5
        """)

        rows = cursor.fetchall()

        for index, row in enumerate(rows, start=1):

            logger.info(
                f"{index}. "
                f"Transaction={row[0]}, "
                f"User={row[1]}, "
                f"Amount=${row[2]:.2f}, "
                f"Date={row[3]}"
            )

        # ====================================================
        # STEP 8: DATABASE ANALYTICS
        # ====================================================

        logger.info("\n[STEP 8] Database analytics summary")

        cursor.execute(
            "SELECT COUNT(DISTINCT user_name) FROM transactions"
        )
        unique_users = cursor.fetchone()[0]

        cursor.execute(
            "SELECT COUNT(DISTINCT country) FROM transactions"
        )
        unique_countries = cursor.fetchone()[0]

        cursor.execute(
            "SELECT SUM(purchase_amount) FROM transactions"
        )
        total_revenue = cursor.fetchone()[0]

        cursor.execute(
            "SELECT AVG(purchase_amount) FROM transactions"
        )
        average_transaction = cursor.fetchone()[0]

        logger.info(f"Unique Users: {unique_users}")
        logger.info(f"Unique Countries: {unique_countries}")

        if total_revenue is not None:
            logger.info(f"Total Revenue: ${total_revenue:.2f}")
        else:
            logger.info("Total Revenue: No data available")

        if average_transaction is not None:
            logger.info(
                f"Average Transaction: ${average_transaction:.2f}"
            )
        else:
            logger.info("Average Transaction: No data available")

        # ====================================================
        # CLOSE CONNECTION
        # ====================================================

        conn.close()

        logger.info("\n" + "=" * 80)
        logger.info("DATABASE IMPORT COMPLETED SUCCESSFULLY")
        logger.info("=" * 80)

        logger.info(
            "\nYou can now run:\n"
            "python -m uvicorn app.main:app --reload\n"
        )

        return True

    except Exception as e:

        logger.error(f"Database import failed: {e}")

        traceback.print_exc()

        return False


# ============================================================
# SCRIPT ENTRY POINT
# ============================================================

if __name__ == "__main__":

    success = import_csv_to_db()

    exit(0 if success else 1)