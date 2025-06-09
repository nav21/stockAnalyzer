import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

EODHD_API_KEY = os.getenv('EODHD_API_KEY')
BASE_URL = 'https://eodhd.com/api/news'

def get_apple_news():
    """Fetch news about Apple from EODHD."""
    try:
        params = {
            'api_token': EODHD_API_KEY,
            's': 'AAPL.US',  # Apple stock symbol
            'limit': 5,      # Get top 5 most relevant news
            'offset': 0
        }
        
        response = requests.get(BASE_URL, params=params)
          # --- Added debugging print statements ---
        print(f"API Response Status Code: {response.status_code}")
    #    print(f"API Response Text: {response.text}")
        # --- End of added debugging print statements ---

        data = response.json()
        
        if isinstance(data, list):
            return data
        else:
            print(f"Error fetching news: {data.get('message', 'Unknown error')}")
            # --- Added debugging print statement for the full error data ---
         #   print(f"Full API Error Data: {data}")
            # --- End of added debugging print statement ---
            return []
            
    except Exception as e:
        print(f"Error fetching news: {str(e)}")
        return [] 