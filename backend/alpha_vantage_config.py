import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')
BASE_URL = 'https://www.alphavantage.co/query'

def get_stock_price(symbol):
    """Fetch the latest stock price from Alpha Vantage."""
    try:
        params = {
            'function': 'GLOBAL_QUOTE',
            'symbol': symbol,
            'apikey': ALPHA_VANTAGE_API_KEY
        }
        
        response = requests.get(BASE_URL, params=params)
  # --- ADDED DEBUGGING PRINTS ---
        print(f"DEBUG: Alpha Vantage Response Status Code: {response.status_code}")
        print(f"DEBUG: Alpha Vantage Raw Response Text: {response.text}")
        # --- END ADDED DEBUGGING PRINTS ---

        data = response.json()
        
        # --- ADDED DEBUGGING PRINT ---
        print(f"DEBUG: Alpha Vantage Parsed JSON Data: {data}")
        # --- END ADDED DEBUGGING PRINT ---        
        if 'Global Quote' in data:
            return float(data['Global Quote']['05. price'])
        else:
            print(f"Error fetching price for {symbol}: {data.get('Note', 'Unknown error')}")
            return None
            
    except Exception as e:
        print(f"Error fetching price for {symbol}: {str(e)}")
        return None 