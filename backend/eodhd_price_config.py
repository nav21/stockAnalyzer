import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

EODHD_API_KEY = os.getenv('EODHD_API_KEY')
# EODHD endpoint for Real-Time/Intraday data (which often includes delayed data for free tier)
BASE_URL = 'https://eodhd.com/api/real-time/'

def get_stock_price(symbol):
    """Fetch the latest stock price from Alpha Vantage."""
    if not EODHD_API_KEY:
        print("Error: EODHD_API_KEY not found in environment variables.")
        return None

    # EODHD Real-Time API often requires the exchange suffix, e.g., AAPL.US, in the URL path.
    # Adjust this logic if you track stocks from other exchanges.
    full_symbol = f"{symbol.upper()}.US" 

    try:
        params = {
            'api_token': EODHD_API_KEY,
            'fmt': 'json', # Request JSON format explicitly
        }
        
        # EODHD Real-Time API puts the symbol directly in the URL path for single symbol queries
        response = requests.get(f"{BASE_URL}{full_symbol}", params=params)

        # Debugging prints
        print(f"DEBUG: EODHD Real-Time Response Status Code for {full_symbol}: {response.status_code}")
        print(f"DEBUG: EODHD Real-Time Raw Response Text for {full_symbol}: {response.text}")

        # EODHD API often returns an error message or specific structure if symbol not found
        if response.status_code != 200:
            print(f"Error fetching price for {full_symbol}: HTTP Status {response.status_code}. Response: {response.text}")
            return None

        data = response.json()
        
        # Debugging print
        print(f"DEBUG: EODHD Real-Time Parsed JSON Data for {full_symbol}: {data}")
        
        # The Real-Time API returns a dictionary for a single stock, not a list.
        # The price is typically in the 'close' key for the latest trade.
        if isinstance(data, dict) and 'close' in data:
            price = float(data['close'])
            print(f"Successfully fetched price for {full_symbol}: {price}")
            return price
        else:
            # Handle cases where data is not a dict or 'close' key is missing
            print(f"Error fetching price for {full_symbol}: Unexpected data format or missing 'close' price. Data: {data}")
            return None
            
    except requests.exceptions.RequestException as req_err:
        print(f"Network or request error fetching price for {full_symbol}: {req_err}")
        return None
    except (ValueError, KeyError) as parse_err: # Removed IndexError as it's no longer a list
        print(f"Data parsing error for {full_symbol}: {parse_err}. Raw data: {response.text}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred fetching price for {full_symbol}: {str(e)}")
        return None