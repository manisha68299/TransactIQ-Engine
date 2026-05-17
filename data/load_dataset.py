import pandas as pd
import numpy as np
import sqlite3
from pathlib import Path
from datetime import datetime
import logging
import sys

# Configure logging with UTF-8 encoding for Windows compatibility
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data_load.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Configuration
DATA_DIR = Path('data')
DATABASE_PATH = Path('ecommerce.db')
PROCESSED_CSV_PATH = DATA_DIR / 'sample_transactions.csv'

# Column mapping - MATCHES ACTUAL CSV COLUMNS
COLUMNS_TO_KEEP = {
    'Transaction_ID': 'transaction_id',
    'User_Name': 'user_name',
    'Country': 'country',
    'Product_Category': 'product_category',
    'Purchase_Amount': 'purchase_amount',
    'Payment_Method': 'payment_method',
    'Transaction_Date': 'transaction_date'
}


def ensure_data_directory():
    """Create data directory if it doesn't exist."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    logger.info(f"[OK] Data directory ensured at {DATA_DIR}")


def load_raw_data():
    """Load CSV data from sample_transactions.csv using Pandas."""
    try:
        if not PROCESSED_CSV_PATH.exists():
            logger.error(f"[ERROR] CSV file not found at {PROCESSED_CSV_PATH}")
            logger.error("[ERROR] Please ensure sample_transactions.csv exists in the data folder")
            return None
        
        logger.info(f"[PROCESS] Loading data from {PROCESSED_CSV_PATH}...")
        df = pd.read_csv(PROCESSED_CSV_PATH)
        logger.info(f"[OK] Loaded {len(df)} records from CSV")
        logger.info(f"[OK] Original columns: {list(df.columns)}")
        return df
        
    except Exception as e:
        logger.error(f"[ERROR] Error loading raw data: {e}")
        import traceback
        traceback.print_exc()
        return None


def clean_data(df):
    """
    Clean and normalize data.
    
    Operations:
    - Remove duplicate transactions
    - Handle missing values
    - Normalize column names
    - Remove unnecessary columns (Age, etc.)
    - Convert data types
    - Validate data ranges
    """
    if df is None:
        return None
    
    logger.info("[PROCESS] Starting data cleaning process...")
    original_count = len(df)
    
    try:
        # Step 1: Remove duplicates based on Transaction_ID
        if 'Transaction_ID' in df.columns:
            df = df.drop_duplicates(subset=['Transaction_ID'], keep='first')
            removed_dupes = original_count - len(df)
            logger.info(f"[OK] Removed duplicates: {removed_dupes} records")
        else:
            logger.info("[OK] No duplicates removed (Transaction_ID column not found)")
        
        # Step 2: Keep only useful columns from the mapping
        available_columns = [col for col in COLUMNS_TO_KEEP.keys() if col in df.columns]
        if available_columns:
            df = df[available_columns]
            logger.info(f"[OK] Kept useful columns: {available_columns}")
        else:
            logger.info("[WARNING] No columns matched the mapping. Using all columns.")
        
        # Step 3: Rename columns to normalized names
        rename_map = {k: v for k, v in COLUMNS_TO_KEEP.items() if k in df.columns}
        if rename_map:
            df = df.rename(columns=rename_map)
            logger.info(f"[OK] Renamed columns to: {list(df.columns)}")
        
        # Step 4: Handle missing values
        initial_rows = len(df)
        df = df.dropna()
        removed_null = initial_rows - len(df)
        if removed_null > 0:
            logger.info(f"[OK] Removed rows with missing values: {removed_null} records")
        
        # Step 5: Remove rows with zero or negative amounts
        if 'purchase_amount' in df.columns:
            before_amount_filter = len(df)
            df = df[df['purchase_amount'] > 0]
            removed_invalid = before_amount_filter - len(df)
            if removed_invalid > 0:
                logger.info(f"[OK] Removed transactions with non-positive amounts: {removed_invalid}")
        
        # Step 6: Convert data types
        if 'transaction_id' in df.columns:
            df['transaction_id'] = df['transaction_id'].astype(str)
        if 'user_name' in df.columns:
            df['user_name'] = df['user_name'].astype(str)
        if 'country' in df.columns:
            df['country'] = df['country'].astype(str)
        if 'product_category' in df.columns:
            df['product_category'] = df['product_category'].astype(str)
        if 'purchase_amount' in df.columns:
            df['purchase_amount'] = pd.to_numeric(df['purchase_amount'], errors='coerce')
        if 'payment_method' in df.columns:
            df['payment_method'] = df['payment_method'].astype(str)
        if 'transaction_date' in df.columns:
            df['transaction_date'] = pd.to_datetime(df['transaction_date'], errors='coerce')
        logger.info(f"[OK] Converted data types")
        
        # Step 7: Normalize string columns
        if 'country' in df.columns:
            df['country'] = df['country'].str.strip().str.title()
        if 'product_category' in df.columns:
            df['product_category'] = df['product_category'].str.strip().str.title()
        if 'payment_method' in df.columns:
            df['payment_method'] = df['payment_method'].str.strip().str.lower()
        if 'user_name' in df.columns:
            df['user_name'] = df['user_name'].str.strip()
        logger.info(f"[OK] Normalized string columns")
        
        # Step 8: Validate amount ranges
        if 'purchase_amount' in df.columns:
            before_range = len(df)
            df = df[(df['purchase_amount'] > 0.01) & (df['purchase_amount'] < 100000)]
            removed_range = before_range - len(df)
            if removed_range > 0:
                logger.info(f"[OK] Validated amount ranges (0.01 to 100000): Removed {removed_range}")
        
        # Step 9: Remove invalid dates
        if 'transaction_date' in df.columns:
            before_date = len(df)
            df = df[df['transaction_date'].notna()]
            removed_date = before_date - len(df)
            if removed_date > 0:
                logger.info(f"[OK] Validated transaction dates: Removed {removed_date}")
        
        # Step 10: Reset index
        df = df.reset_index(drop=True)
        
        logger.info(f"\n[OK] Cleaning complete: {original_count} --> {len(df)} records")
        logger.info(f"[OK] Final shape: {df.shape}")
        logger.info(f"[OK] Final columns: {list(df.columns)}")
        
        return df
        
    except Exception as e:
        logger.error(f"[ERROR] Error during data cleaning: {e}")
        import traceback
        traceback.print_exc()
        return None


def load_to_database(df):
    """Load cleaned data into SQLite database."""
    try:
        if df is None:
            return False
        
        logger.info(f"[PROCESS] Loading data into SQLite database at {DATABASE_PATH}...")
        
        # Connect to database
        conn = sqlite3.connect(str(DATABASE_PATH))
        
        # Load data into 'transactions' table with proper schema
        df.to_sql('transactions', conn, if_exists='replace', index=False)
        
        # Get row count
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM transactions")
        count = cursor.fetchone()[0]
        
        # Get column info
        cursor.execute("PRAGMA table_info(transactions)")
        columns = cursor.fetchall()
        
        conn.commit()
        conn.close()
        
        logger.info(f"[OK] Loaded {count} records into SQLite database")
        logger.info(f"[OK] Database location: {DATABASE_PATH}")
        logger.info(f"[OK] Table columns: {[col[1] for col in columns]}")
        return True
        
    except Exception as e:
        logger.error(f"[ERROR] Error loading to database: {e}")
        import traceback
        traceback.print_exc()
        return False


def display_data_summary(df):
    """Display summary statistics of the dataset."""
    if df is None:
        return
    
    logger.info("\n" + "="*80)
    logger.info("DATA SUMMARY")
    logger.info("="*80)
    
    logger.info(f"\nDataset Shape: {df.shape}")
    logger.info(f"\nFirst 5 Rows:")
    logger.info(f"\n{df.head()}")
    
    logger.info(f"\nData Types:")
    for col, dtype in df.dtypes.items():
        logger.info(f"  {col}: {dtype}")
    
    logger.info(f"\nDescriptive Statistics:")
    logger.info(f"\n{df.describe()}")
    
    if 'country' in df.columns:
        logger.info(f"\nCategorical Data Summary:")
        logger.info(f"  - Unique Countries: {df['country'].nunique()}")
    
    if 'product_category' in df.columns:
        logger.info(f"  - Unique Product Categories: {df['product_category'].nunique()}")
    
    if 'payment_method' in df.columns:
        logger.info(f"  - Unique Payment Methods: {df['payment_method'].nunique()}")
    
    if 'user_name' in df.columns:
        logger.info(f"  - Unique Users: {df['user_name'].nunique()}")
    
    if 'purchase_amount' in df.columns:
        logger.info(f"\nAmount Statistics:")
        logger.info(f"  - Min: ${df['purchase_amount'].min():.2f}")
        logger.info(f"  - Max: ${df['purchase_amount'].max():.2f}")
        logger.info(f"  - Mean: ${df['purchase_amount'].mean():.2f}")
        logger.info(f"  - Median: ${df['purchase_amount'].median():.2f}")
        logger.info(f"  - Std Dev: ${df['purchase_amount'].std():.2f}")
        logger.info(f"  - Total Revenue: ${df['purchase_amount'].sum():.2f}")
    
    if 'transaction_date' in df.columns:
        logger.info(f"\nDate Range:")
        logger.info(f"  - From: {df['transaction_date'].min()}")
        logger.info(f"  - To: {df['transaction_date'].max()}")
    
    if 'payment_method' in df.columns:
        logger.info(f"\nPayment Methods Distribution:")
        payment_dist = df['payment_method'].value_counts()
        for method, count in payment_dist.items():
            percentage = (count / len(df)) * 100
            logger.info(f"  - {method}: {count} ({percentage:.2f}%)")
    
    if 'country' in df.columns:
        logger.info(f"\nTop 15 Countries by Transaction Count:")
        country_dist = df['country'].value_counts().head(15)
        for country, count in country_dist.items():
            logger.info(f"  - {country}: {count}")
    
    if 'product_category' in df.columns:
        logger.info(f"\nTop 10 Product Categories by Transaction Count:")
        category_dist = df['product_category'].value_counts().head(10)
        for category, count in category_dist.items():
            logger.info(f"  - {category}: {count}")
    
    logger.info("\n" + "="*80 + "\n")


def main():
    """Main execution flow."""
    logger.info("="*80)
    logger.info("E-COMMERCE TRANSACTIONS DATASET LOADER")
    logger.info("="*80)
    logger.info(f"Start time: {datetime.now()}\n")
    
    try:
        # Step 1: Ensure data directory exists
        logger.info("[STEP 1] Ensuring data directory...")
        ensure_data_directory()
        
        # Step 2: Load raw data from existing CSV
        logger.info("\n[STEP 2] Loading data from sample_transactions.csv...")
        df = load_raw_data()
        if df is None:
            logger.error("[ERROR] Failed to load raw data. Exiting.")
            return False
        
        # Step 3: Clean data
        logger.info("\n[STEP 3] Cleaning and normalizing data...")
        df = clean_data(df)
        if df is None:
            logger.error("[ERROR] Failed to clean data. Exiting.")
            return False
        
        # Step 4: Load to database
        logger.info("\n[STEP 4] Loading data into SQLite database...")
        if not load_to_database(df):
            logger.error("[ERROR] Failed to load data into database. Exiting.")
            return False
        
        # Step 5: Display summary
        logger.info("\n[STEP 5] Displaying data summary...")
        display_data_summary(df)
        
        logger.info("="*80)
        logger.info("[SUCCESS] DATASET LOADING COMPLETED SUCCESSFULLY")
        logger.info("="*80)
        logger.info(f"End time: {datetime.now()}")
        logger.info(f"\n[SUCCESS] You can now run: python -m uvicorn app.main:app --reload\n")
        
        return True
        
    except Exception as e:
        logger.error(f"[ERROR] Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)