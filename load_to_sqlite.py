# load_to_sqlite.py
import sqlite3
import pandas as pd

DB_NAME = 'transactions.db'
TABLE_NAME = 'transactions'
CSV_FILE = 'transactions.csv' # This is the cleaned expenses CSV

def load_data_to_sqlite():
    """
    Loads cleaned transaction data from CSV into an SQLite database.
    """
    try:
        df = pd.read_csv(CSV_FILE)
        print(f"Successfully read {CSV_FILE}")
    except FileNotFoundError:
        print(f"Error: {CSV_FILE} not found. Please run process_transactions.py first.")
        return

    if df.empty:
        print(f"{CSV_FILE} is empty. No data to load.")
        return

    # Ensure date column is in a format SQLite understands well (TEXT as YYYY-MM-DD)
    # If it's already datetime objects from pandas, to_sql handles it.
    # If it's strings, ensure they are ISO format.
    # df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d') # Uncomment if issues with date type

    try:
        print(f"Connecting to SQLite database: {DB_NAME}...")
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        print("Successfully connected to SQLite.")

        # Create table - IF NOT EXISTS ensures it's only created once
        # Define schema explicitly for better control
        # Note: Plaid transaction_id is a good candidate for PRIMARY KEY if unique and always present
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            transaction_id TEXT PRIMARY KEY,
            date TEXT, 
            amount REAL, 
            category TEXT,
            merchant_name TEXT,
            pending BOOLEAN
        )
        """
        print(f"Executing: CREATE TABLE IF NOT EXISTS {TABLE_NAME} ...")
        cursor.execute(create_table_query)
        print(f"Table '{TABLE_NAME}' ensured to exist.")

        # Load data into SQL table
        # 'replace' will drop the table first if it exists and create a new one.
        # 'append' would add new rows. Consider your use case.
        # For this ETL example, 'replace' is often suitable for a fresh load.
        print(f"Loading data into '{TABLE_NAME}' table (using if_exists='replace')...")
        df.to_sql(TABLE_NAME, conn, if_exists='replace', index=False)
        conn.commit()
        print(f"Data successfully loaded into '{TABLE_NAME}'.")

    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()
            print("SQLite connection closed.")

if __name__ == "__main__":
    load_data_to_sqlite()