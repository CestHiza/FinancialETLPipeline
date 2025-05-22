# process_transactions.py
import pandas as pd

def clean_and_transform_data(input_csv='raw_transactions.csv'):
    """
    Cleans the raw transaction data and creates a spending summary.
    """
    try:
        df = pd.read_csv(input_csv)
        print(f"Successfully read {input_csv}")
    except FileNotFoundError:
        print(f"Error: {input_csv} not found. Please run fetch_plaid_transactions.py first.")
        return None, None

    print("\n--- Original DataFrame info ---")
    df.info()
    print(df.head())

    # Data Cleaning
    # Fill missing categories (already handled by join, but good as a fallback)
    df['category'] = df['category'].fillna('Other')

    # Ensure 'date' column is in datetime format
    df['date'] = pd.to_datetime(df['date'])

    # Plaid typically returns expenses as positive amounts and income/credits as negative.
    # The filter `df['amount'] > 0` keeps expenses (outflows).
    # If you want to analyze income, you might filter for `df['amount'] < 0`
    # and then take the absolute value `df['amount'] = df['amount'].abs()`.
    
    df_expenses = df[df['amount'] > 0].copy() # Create a copy to avoid SettingWithCopyWarning
    print(f"\nFiltered down to {len(df_expenses)} expense transactions (amount > 0).")

    if df_expenses.empty:
        print("No expense transactions found after filtering.")
        return df_expenses, None # Return empty df and None for summary

    # Data Transformation
    # Create a spending summary by category
    # We use df_expenses for this summary
    print("\nGenerating spending summary by category...")
    spending_summary = df_expenses.groupby('category')['amount'].sum().reset_index()
    spending_summary = spending_summary.sort_values(by='amount', ascending=False)

    print("\n--- Cleaned Transactions DataFrame (First 5 rows of expenses) ---")
    print(df_expenses.head())
    
    print("\n--- Spending Summary (First 5 rows) ---")
    print(spending_summary.head())

    # Save cleaned data and summary to CSV
    df_expenses.to_csv('transactions.csv', index=False)
    print("\nCleaned expense transactions saved to transactions.csv")
    
    spending_summary.to_csv('spending_summary.csv', index=False)
    print("Spending summary saved to spending_summary.csv")
    
    return df_expenses, spending_summary

if __name__ == "__main__":
    cleaned_df, summary_df = clean_and_transform_data()
    if cleaned_df is not None:
        print("\nData cleaning and transformation complete.")
    else:
        print("\nData cleaning and transformation failed or produced no data.")