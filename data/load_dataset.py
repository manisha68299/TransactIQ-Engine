import pandas as pd
import numpy as np
import sqlite3
from pathlib import Path
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data_load.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
DATA_DIR = Path('data')
DATABASE_PATH = Path('ecommerce.db')
RAW_CSV_PATH = DATA_DIR / 'ecommerce_transactions_50k.csv'
PROCESSED_CSV_PATH = DATA_DIR / 'sample_transactions.csv'

# Column mapping from raw dataset to processed dataset
COLUMNS_TO_KEEP = {
    'Transaction_ID': 'transaction_id',  # Renames to lowercase
    'User_Name': 'user_name',
    'Country': 'country',
    'Product_Category': 'product_category',
    'Purchase_Amount': 'amount',
    'Payment_Method': 'payment_method',
    'Transaction_Date': 'transaction_date'
}


def ensure_data_directory():
    """Create data directory if it doesn't exist."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    logger.info(f"✓ Data directory ensured at {DATA_DIR}")


def download_dataset():
    """
    Download dataset from Kaggle.
    
    Before running:
    1. Install kaggle: pip install kaggle
    2. Download API token from https://www.kaggle.com/settings/account
    3. Place kaggle.json in ~/.kaggle/
    
    To download manually:
    Visit: https://www.kaggle.com/datasets/shriyabhatt/ecommerce-transactions-dataset
    Download and place in data/ folder
    """
    try:
        # Check if file already exists
        if RAW_CSV_PATH.exists():
            logger.info(f"✓ Dataset already exists at {RAW_CSV_PATH}")
            return True
        
        # Try to download using Kaggle API
        try:
            from kaggle.api.kaggle_api_extended import KaggleApi
            
            logger.info("Attempting to download dataset from Kaggle...")
            api = KaggleApi()
            api.authenticate()
            
            # Download dataset
            api.dataset_download_files(
                'shriyabhatt/ecommerce-transactions-dataset',
                path=DATA_DIR,
                unzip=True
            )
            logger.info("✓ Dataset downloaded successfully from Kaggle")
            return True
            
        except Exception as e:
            logger.warning(f"Could not download from Kaggle: {e}")
            logger.info("Please download manually from: https://www.kaggle.com/datasets/shriyabhatt/ecommerce-transactions-dataset")
            return False
            
    except Exception as e:
        logger.error(f"Error in download_dataset: {e}")
        return False


def load_raw_data():
    """Load raw CSV data using Pandas."""
    try:
        if not RAW_CSV_PATH.exists():
            logger.error(f"CSV file not found at {RAW_CSV_PATH}")
            logger.info("Please download the dataset from Kaggle first")
            return None
        
        logger.info(f"Loading raw data from {RAW_CSV_PATH}...")
        df = pd.read_csv(RAW_CSV_PATH)
        logger.info(f"✓ Loaded {len(df)} records from CSV")
        logger.info(f"✓ Original columns: {list(df.columns)}")
        return df
        
    except Exception as e:
        logger.error(f"Error loading raw data: {e}")
        return None


def clean_data(df):
    """
    Clean and normalize data.
    
    Operations:
    - Remove duplicate transactions
    - Handle missing values
    - Normalize column names
    - Remove unnecessary columns
    - Convert data types
    - Validate data ranges
    """
    if df is None:
        return None
    
    logger.info("Starting data cleaning process...")
    original_count = len(df)
    
    try:
        # Step 1: Remove duplicates based on Transaction_ID
        df = df.drop_duplicates(subset=['Transaction_ID'], keep='first')
        logger.info(f"✓ Removed duplicates: {original_count - len(df)} records")
        
        # Step 2: Keep only useful columns
        available_columns = [col for col in COLUMNS_TO_KEEP.keys() if col in df.columns]
        df = df[available_columns]
        logger.info(f"✓ Kept useful columns: {available_columns}")
        
        # Step 3: Rename columns to normalized names
        rename_map = {k: v for k, v in COLUMNS_TO_KEEP.items() if k in df.columns}
        df = df.rename(columns=rename_map)
        logger.info(f"✓ Renamed columns to: {list(df.columns)}")
        
        # Step 4: Handle missing values
        missing_before = df.isnull().sum().sum()
        df = df.dropna()
        missing_after = df.isnull().sum().sum()
        logger.info(f"✓ Removed rows with missing values: {len(df[df.isnull().any(axis=1)])}")
        
        # Step 5: Remove rows with zero or negative amounts
        df = df[df['amount'] > 0]
        logger.info(f"✓ Removed transactions with non-positive amounts")
        
        # Step 6: Convert data types
        df['transaction_id'] = df['transaction_id'].astype(str)
        df['user_name'] = df['user_name'].astype(str)
        df['country'] = df['country'].astype(str)
        df['product_category'] = df['product_category'].astype(str)
        df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
        df['payment_method'] = df['payment_method'].astype(str)
        df['transaction_date'] = pd.to_datetime(df['transaction_date'], errors='coerce')
        logger.info(f"✓ Converted data types")
        
        # Step 7: Normalize string columns (trim whitespace, lowercase where appropriate)
        df['country'] = df['country'].str.strip().str.title()
        df['product_category'] = df['product_category'].str.strip().str.title()
        df['payment_method'] = df['payment_method'].str.strip().str.lower()
        df['user_name'] = df['user_name'].str.strip()
        logger.info(f"✓ Normalized string columns")
        
        # Step 8: Validate amount ranges (realistic e-commerce amounts)
        df = df[(df['amount'] > 0.01) & (df['amount'] < 100000)]
        logger.info(f"✓ Validated amount ranges (0.01 to 100000)")
        
        # Step 9: Remove invalid dates
        df = df[df['transaction_date'].notna()]
        logger.info(f"✓ Validated transaction dates")
        
        # Step 10: Reset index
        df = df.reset_index(drop=True)
        
        logger.info(f"✓ Cleaning complete: {original_count} → {len(df)} records")
        logger.info(f"✓ Final shape: {df.shape}")
        logger.info(f"✓ Final columns: {list(df.columns)}")
        logger.info(f"✓ Data types:\n{df.dtypes}")
        
        return df
        
    except Exception as e:
        logger.error(f"Error during data cleaning: {e}")
        return None


def save_processed_data(df):
    """Save cleaned data to CSV."""
    try:
        if df is None:
            return False
        
        logger.info(f"Saving processed data to {PROCESSED_CSV_PATH}...")
        df.to_csv(PROCESSED_CSV_PATH, index=False)
        logger.info(f"✓ Processed data saved: {len(df)} records")
        return True
        
    except Exception as e:
        logger.error(f"Error saving processed data: {e}")
        return False


def load_to_database(df):
    """Load cleaned data into SQLite database."""
    try:
        if df is None:
            return False
        
        logger.info(f"Loading data into SQLite database at {DATABASE_PATH}...")
        
        # Connect to database
        conn = sqlite3.connect(DATABASE_PATH)
        
        # Load data into 'transactions' table
        df.to_sql('transactions', conn, if_exists='replace', index=False)
        
        # Get row count
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM transactions")
        count = cursor.fetchone()[0]
        
        conn.commit()
        conn.close()
        
        logger.info(f"✓ Loaded {count} records into SQLite database")
        return True
        
    except Exception as e:
        logger.error(f"Error loading to database: {e}")
        return False


def display_data_summary(df):
    """Display summary statistics of the dataset."""
    if df is None:
        return
    
    logger.info("\n" + "="*80)
    logger.info("DATA SUMMARY")
    logger.info("="*80)
    
    logger.info(f"\nDataset Shape: {df.shape}")
    logger.info(f"\nColumn Information:")
    logger.info(f"\n{df.info()}")
    
    logger.info(f"\nFirst 5 Rows:")
    logger.info(f"\n{df.head()}")
    
    logger.info(f"\nDescriptive Statistics (Numeric Columns):")
    logger.info(f"\n{df.describe()}")
    
    logger.info(f"\nCategorical Data Summary:")
    logger.info(f"  - Unique Countries: {df['country'].nunique()}")
    logger.info(f"  - Unique Product Categories: {df['product_category'].nunique()}")
    logger.info(f"  - Unique Payment Methods: {df['payment_method'].nunique()}")
    logger.info(f"  - Unique Users: {df['user_name'].nunique()}")
    
    logger.info(f"\nAmount Statistics:")
    logger.info(f"  - Min: ${df['amount'].min():.2f}")
    logger.info(f"  - Max: ${df['amount'].max():.2f}")
    logger.info(f"  - Mean: ${df['amount'].mean():.2f}")
    logger.info(f"  - Median: ${df['amount'].median():.2f}")
    logger.info(f"  - Std Dev: ${df['amount'].std():.2f}")
    
    logger.info(f"\nDate Range:")
    logger.info(f"  - From: {df['transaction_date'].min()}")
    logger.info(f"  - To: {df['transaction_date'].max()}")
    
    logger.info(f"\nPayment Methods Distribution:")
    payment_dist = df['payment_method'].value_counts()
    for method, count in payment_dist.items():
        percentage = (count / len(df)) * 100
        logger.info(f"  - {method}: {count} ({percentage:.2f}%)")
    
    logger.info(f"\nTop 10 Countries by Transaction Count:")
    country_dist = df['country'].value_counts().head(10)
    for country, count in country_dist.items():
        logger.info(f"  - {country}: {count}")
    
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
    logger.info(f"Start time: {datetime.now()}")
    
    try:
        # Step 1: Ensure data directory exists
        ensure_data_directory()
        
        # Step 2: Download dataset (optional - can be done manually)
        logger.info("\n[STEP 1] Downloading dataset...")
        download_dataset()
        
        # Step 3: Load raw data
        logger.info("\n[STEP 2] Loading raw data...")
        df = load_raw_data()
        if df is None:
            logger.error("Failed to load raw data. Exiting.")
            return False
        
        # Step 4: Clean data
        logger.info("\n[STEP 3] Cleaning and normalizing data...")
        df = clean_data(df)
        if df is None:
            logger.error("Failed to clean data. Exiting.")
            return False
        
        # Step 5: Save processed data
        logger.info("\n[STEP 4] Saving processed data...")
        if not save_processed_data(df):
            logger.error("Failed to save processed data. Exiting.")
            return False
        
        # Step 6: Load to database
        logger.info("\n[STEP 5] Loading data into SQLite database...")
        if not load_to_database(df):
            logger.error("Failed to load data into database. Exiting.")
            return False
        
        # Step 7: Display summary
        logger.info("\n[STEP 6] Displaying data summary...")
        display_data_summary(df)
        
        logger.info("="*80)
        logger.info("✓ DATASET LOADING COMPLETED SUCCESSFULLY")
        logger.info("="*80)
        logger.info(f"End time: {datetime.now()}")
        logger.info(f"\nYou can now run: python -m uvicorn app.main:app --reload")
        
        return True
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)