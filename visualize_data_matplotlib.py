# visualize_data_matplotlib.py
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

SUMMARY_CSV = 'spending_summary.csv'
TRANSACTIONS_CSV = 'transactions.csv' # Cleaned expenses

def plot_spending_by_category():
    """
    Plots spending by category from spending_summary.csv.
    """
    try:
        df_summary = pd.read_csv(SUMMARY_CSV)
    except FileNotFoundError:
        print(f"Error: {SUMMARY_CSV} not found. Please run process_transactions.py first.")
        return

    if df_summary.empty:
        print(f"{SUMMARY_CSV} is empty. No data to plot.")
        return

    print("Plotting spending by category...")
    plt.figure(figsize=(12, 8))
    # Take top N categories for better readability if there are many
    top_n = 15 
    df_plot = df_summary.head(top_n)

    bars = plt.bar(df_plot['category'], df_plot['amount'], color='skyblue')
    plt.xlabel('Category', fontsize=12)
    plt.ylabel('Amount ($)', fontsize=12)
    plt.title(f'Top {top_n} Spending by Category', fontsize=15)
    plt.xticks(rotation=45, ha="right", fontsize=10)
    plt.yticks(fontsize=10)
    plt.tight_layout() # Adjust layout to prevent labels from overlapping
    
    # Add labels on top of bars
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2.0, yval + 0.05 * yval, f'${yval:,.2f}', ha='center', va='bottom', fontsize=9)


    plt.savefig('spending_by_category.png')
    print(f"Spending by category plot saved to spending_by_category.png")
    plt.close() # Close the plot to free memory

def plot_daily_spending_trend():
    """
    Plots the trend of daily spending from transactions.csv.
    """
    try:
        df_transactions = pd.read_csv(TRANSACTIONS_CSV)
    except FileNotFoundError:
        print(f"Error: {TRANSACTIONS_CSV} not found. Please run process_transactions.py first.")
        return

    if df_transactions.empty:
        print(f"{TRANSACTIONS_CSV} is empty. No data to plot.")
        return

    print("Plotting daily spending trend...")
    df_transactions['date'] = pd.to_datetime(df_transactions['date'])
    daily_spending = df_transactions.groupby('date')['amount'].sum().reset_index()
    daily_spending = daily_spending.sort_values(by='date')

    plt.figure(figsize=(14, 7))
    plt.plot(daily_spending['date'], daily_spending['amount'], marker='o', linestyle='-', color='teal')
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Total Spending ($)', fontsize=12)
    plt.title('Daily Spending Trend', fontsize=15)
    plt.xticks(rotation=45, fontsize=10)
    plt.yticks(fontsize=10)
    plt.grid(True, linestyle='--', alpha=0.7)
    
    # Format the x-axis dates for better readability
    ax = plt.gca()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator(minticks=5, maxticks=10)) # Adjust number of ticks

    plt.tight_layout()
    plt.savefig('daily_spending_trend.png')
    print(f"Daily spending trend plot saved to daily_spending_trend.png")
    plt.close()


if __name__ == "__main__":
    plot_spending_by_category()
    plot_daily_spending_trend()