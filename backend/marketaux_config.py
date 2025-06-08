import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

MARKETAUX_API_KEY = os.getenv('MARKETAUX_API_KEY')
BASE_URL = 'https://api.marketaux.com/v1/news/all'

def get_apple_news():
    """Fetch news about Apple from Marketaux."""
    try:
        params = {
            'api_token': MARKETAUX_API_KEY,
            'q': 'Apple Inc OR AAPL',
            'language': 'en',
            'limit': 2,  # Get top 2 most relevant news
            'exclude_entities': 'false',
            'sentiment': 'true'
        }
        
        response = requests.get(BASE_URL, params=params)
        data = response.json()
        
        if 'data' in data:
            return data['data']
        else:
            print(f"Error fetching news: {data.get('error', 'Unknown error')}")
            return []
            
    except Exception as e:
        print(f"Error fetching news: {str(e)}")
        return [] 