# Financial Transaction ETL Pipeline

This project implements an ETL (Extract, Transform, Load) pipeline for fetching mock financial transactions using the Plaid API (Sandbox), processing the data with Python (Pandas), storing it in an SQLite database, and visualizing insights using Matplotlib.

## Project Overview

The pipeline consists of the following main steps:

1.  **Extract:** Fetches transaction data from the Plaid API's Sandbox environment for a test institution. API keys are managed in a separate `config.py` file (not committed to Git).
2.  **Transform:** Cleans the raw transaction data (e.g., handles missing values, filters for expenses) and generates a spending summary by category.
3.  **Load:** Stores the cleaned transaction data into an SQLite database.
4.  **Visualize:** Generates plots for spending by category and daily spending trends using Matplotlib. An option to use Tableau with the generated CSV files is also available.

## Project Structure


FinancialETLPipeline/
├── .gitignore                  # Specifies intentionally untracked files (including config.py)
├── config.py                   # Local configuration for API keys (NOT COMMITTED TO GIT)
├── fetch_plaid_transactions.py # Script to fetch data from Plaid API
├── process_transactions.py     # Script to clean and transform transaction data
├── load_to_sqlite.py           # Script to load data into SQLite
├── visualize_data_matplotlib.py # Script for Matplotlib visualizations
├── raw_transactions.csv        # Output: Raw data from Plaid (created by fetch_)
├── transactions.csv            # Output: Cleaned expense data (created by process_)
├── spending_summary.csv        # Output: Spending summary by category (created by process_)
├── transactions.db             # Output: SQLite database (created by load_)
├── spending_by_category.png    # Output: Matplotlib plot (created by visualize_)
├── daily_spending_trend.png    # Output: Matplotlib plot (created by visualize_)
└── venv/                       # Python virtual environment (ignored by Git)


## Prerequisites

* Python (3.6+ recommended)
* Plaid Developer Account & Sandbox API Keys (`CLIENT_ID`, `SECRET`)
* Git
* Optional: Tableau Public or Tableau Desktop

## Setup and Installation

1.  **Clone the repository (if applicable):**
    ```bash
    git clone [https://github.com/YOUR_USERNAME/FinancialETLPipeline.git](https://github.com/YOUR_USERNAME/FinancialETLPipeline.git)
    cd FinancialETLPipeline
    ```

2.  **Create and activate a Python virtual environment:**
    ```bash
    python -m venv venv
    # On Windows
    .\venv\Scripts\activate
    # On macOS/Linux
    # source venv/bin/activate
    ```

3.  **Install Python libraries:**
    ```bash
    pip install plaid-python pandas matplotlib
    ```
    *(Consider creating a `requirements.txt` file for easier dependency management: `pip freeze > requirements.txt`)*

4.  **Configure Plaid API Keys:**
    * Create a file named `config.py` in the root of your project directory.
    * Add your Plaid API keys to `config.py` like this:
      ```python
      # config.py
      PLAID_CLIENT_ID = 'your-actual-plaid-client-id'
      PLAID_SECRET = 'your-actual-plaid-sandbox-secret'
      PLAID_ENV_NAME = 'sandbox' # Or 'development', 'production'
      ```
    * **SECURITY WARNING:** The `config.py` file is listed in `.gitignore` and **MUST NOT** be committed to your Git repository. This keeps your API keys private.

## Running the Pipeline

Execute the scripts in the following order from your project's root directory:

1.  **Fetch Raw Transactions from Plaid:**
    ```bash
    python fetch_plaid_transactions.py
    ```
    This will create `raw_transactions.csv`.

2.  **Clean and Transform Data:**
    ```bash
    python process_transactions.py
    ```
    This reads `raw_transactions.csv` and creates `transactions.csv` (cleaned expenses) and `spending_summary.csv`.

3.  **Load Data to SQLite Database:**
    ```bash
    python load_to_sqlite.py
    ```
    This reads `transactions.csv` and loads it into `transactions.db`.

4.  **Visualize Data (Matplotlib):**
    ```bash
    python visualize_data_matplotlib.py
    ```
    This creates `spending_by_category.png` and `daily_spending_trend.png`.

## Visualization with Tableau (Optional)

1.  Open Tableau Desktop or Tableau Public.
2.  Connect to a "Text File".
3.  Select `transactions.csv` to analyze individual transactions or `spending_summary.csv` for aggregated category spending.
4.  Create your desired visualizations (e.g., bar charts for spending by category, trend lines for daily spending).

## Author

* Hiza Mvuendy

## License

(Specify a license if you wish, e.g., MIT License. If not, you can remove this section or state "Proprietary".)
