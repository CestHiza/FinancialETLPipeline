# fetch_plaid_transactions.py
import plaid
import pandas as pd
from plaid.api import plaid_api
from plaid.model.products import Products
# CountryCode is not directly used but good to be aware of for Plaid's internationalization
# from plaid.model.country_code import CountryCode 
from plaid.model.sandbox_public_token_create_request import SandboxPublicTokenCreateRequest
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.transactions_get_request import TransactionsGetRequest
from datetime import datetime, timedelta, date # Ensure date is imported
import time # For adding delays in retry logic

# Attempt to import configuration
try:
    import config
except ImportError:
    print("ERROR: config.py not found. Please create it and add your Plaid API keys.")
    print("Refer to the project documentation for the structure of config.py.")
    exit()

# --- Configuration from config.py ---
PLAID_CLIENT_ID = getattr(config, 'PLAID_CLIENT_ID', None)
PLAID_SECRET = getattr(config, 'PLAID_SECRET', None)
PLAID_ENV_NAME = getattr(config, 'PLAID_ENV_NAME', 'sandbox').lower()


# Determine Plaid environment
if PLAID_ENV_NAME == 'sandbox':
    PLAID_ENV = plaid.Environment.Sandbox
elif PLAID_ENV_NAME == 'development':
    PLAID_ENV = plaid.Environment.Development
elif PLAID_ENV_NAME == 'production':
    PLAID_ENV = plaid.Environment.Production
else:
    print(f"ERROR: Invalid PLAID_ENV_NAME '{PLAID_ENV_NAME}' in config.py. Use 'sandbox', 'development', or 'production'.")
    exit()


# Define the start and end dates for transactions
# Fetch transactions for the last 30 days
end_date_obj = datetime.now().date()  # This is a date object
start_date_obj = end_date_obj - timedelta(days=30) # This is also a date object

def fetch_transactions():
    """
    Fetches mock transactions from Plaid Sandbox API.
    Includes retry logic for "PRODUCT_NOT_READY" errors.
    """
    if not PLAID_CLIENT_ID or PLAID_CLIENT_ID == 'your-plaid-client-id' or \
       not PLAID_SECRET or PLAID_SECRET == 'your-plaid-sandbox-secret':
        print("ERROR: Plaid API keys not configured correctly in config.py.")
        print("Please ensure PLAID_CLIENT_ID and PLAID_SECRET are set.")
        return None

    print(f"Initializing Plaid client for {PLAID_ENV_NAME} environment...")
    configuration = plaid.Configuration(
        host=PLAID_ENV,
        api_key={
            'clientId': PLAID_CLIENT_ID,
            'secret': PLAID_SECRET,
        }
    )
    api_client = plaid.ApiClient(configuration)
    client = plaid_api.PlaidApi(api_client)

    try:
        # Step 1: Create a Sandbox Public Token for a test institution
        pt_request = SandboxPublicTokenCreateRequest(
            institution_id='ins_109512', # Example: First Platypus Bank - Transactions
            initial_products=[Products('transactions')]
        )
        print("Creating sandbox public token...")
        pt_response = client.sandbox_public_token_create(pt_request)
        public_token = pt_response['public_token']
        print(f"Successfully created sandbox public token: {public_token[:10]}...")

        # Step 2: Exchange Public Token for an Access Token
        exchange_request = ItemPublicTokenExchangeRequest(
            public_token=public_token
        )
        print("Exchanging public token for access token...")
        exchange_response = client.item_public_token_exchange(exchange_request)
        access_token = exchange_response['access_token']
        item_id = exchange_response['item_id']
        print(f"Successfully exchanged for access token: {access_token[:10]}... for item_id: {item_id}")

        # Step 3: Fetch Transactions with retry logic
        transactions_request = TransactionsGetRequest(
            access_token=access_token,
            start_date=start_date_obj, 
            end_date=end_date_obj,     
            options={'count': 500}
        )
        
        print(f"Attempting to fetch transactions from {start_date_obj.strftime('%Y-%m-%d')} to {end_date_obj.strftime('%Y-%m-%d')}...")
        
        transactions_response = None
        max_retries = 5
        retry_delay_seconds = 10 # Wait 10 seconds between retries

        for attempt in range(max_retries):
            try:
                transactions_response = client.transactions_get(transactions_request)
                print(f"Successfully fetched initial batch of transactions on attempt {attempt + 1}.")
                break # Exit retry loop on success
            except plaid.ApiException as e:
                error_body_parsed = {}
                error_code = None
                if isinstance(e.body, str):
                    try:
                        import json
                        error_body_parsed = json.loads(e.body)
                        error_code = error_body_parsed.get('error_code')
                    except json.JSONDecodeError:
                        pass # error_code remains None
                
                if error_code == 'PRODUCT_NOT_READY' and attempt < max_retries - 1:
                    print(f"Plaid API Exception (Attempt {attempt + 1}/{max_retries}): PRODUCT_NOT_READY. Retrying in {retry_delay_seconds} seconds...")
                    time.sleep(retry_delay_seconds)
                else:
                    # For other errors or if max retries reached, re-raise the exception
                    raise e 
        
        if transactions_response is None:
            print("Failed to fetch transactions after multiple retries due to PRODUCT_NOT_READY or other issues.")
            return None

        transactions_data = transactions_response['transactions']
        
        # Basic pagination: Keep fetching if more transactions are available
        while len(transactions_data) < transactions_response['total_transactions']:
            if transactions_request.options is None:
                 transactions_request.options = {}
            transactions_request.options['offset'] = len(transactions_data)
            
            print(f"Fetching next page of transactions, offset: {transactions_request.options['offset']}...")
            # No retry logic for subsequent pages, assuming product is ready by now.
            transactions_response = client.transactions_get(transactions_request)
            newly_fetched = transactions_response['transactions']
            if not newly_fetched: 
                print("No more transactions returned in pagination.")
                break
            transactions_data.extend(newly_fetched)
            print(f"Fetched {len(newly_fetched)} more transactions. Total now: {len(transactions_data)}.")

        print(f"Successfully fetched a total of {len(transactions_data)} transactions.")

        data_list = []
        for t in transactions_data:
            category_str = 'Other'
            if t.category and isinstance(t.category, list) and len(t.category) > 0:
                category_str = ', '.join(t.category)
            
            data_list.append({
                'transaction_id': t.transaction_id,
                'date': t.date, 
                'amount': t.amount,
                'category': category_str,
                'merchant_name': t.merchant_name if t.merchant_name else 'N/A',
                'pending': t.pending
            })
        
        df = pd.DataFrame(data_list)
        return df

    except plaid.ApiException as e:
        error_details = "Could not parse error body."
        try:
            if isinstance(e.body, str):
                import json
                error_payload = json.loads(e.body)
                error_details = f"Error Code: {error_payload.get('error_code', 'N/A')}, Message: {error_payload.get('error_message', e.body)}"
            elif hasattr(e, 'body') and hasattr(e.body, 'error_code') and hasattr(e.body, 'error_message'):
                error_details = f"Error Code: {e.body.error_code}, Message: {e.body.error_message}"
            elif hasattr(e, 'body'):
                 error_details = str(e.body)
            else:
                error_details = str(e)
        except Exception as parse_err:
            error_details = f"Original error: {e.body if hasattr(e, 'body') else str(e)}. Parsing error: {parse_err}"
        print(f"Plaid API Exception: {error_details}")
        return None
    except Exception as e:
        import traceback
        print(f"An unexpected error occurred: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return None

if __name__ == "__main__":
    raw_df = fetch_transactions()
    if raw_df is not None and not raw_df.empty:
        print("\n--- Raw Transactions DataFrame (First 5 rows) ---")
        print(raw_df.head())
        raw_df.to_csv('raw_transactions.csv', index=False)
        print("\nRaw transactions saved to raw_transactions.csv")
    elif raw_df is not None and raw_df.empty:
        print("\nNo transactions fetched or an empty DataFrame was returned.")
    else:
        print("\nFailed to fetch transactions.")