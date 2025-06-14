import os
import requests
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

EODHD_API_KEY = os.getenv('EODHD_API_KEY')
BASE_URL = 'https://eodhd.com/api/news'

def get_news(symbol: str, from_date: str = None, to_date: str = None):
    if not to_date:
        to_date = '2025-06-13'
    if not from_date:
        from_date = '2025-05-20'
    
    try:
        params = {
            'api_token': EODHD_API_KEY,
            's': symbol,
            'offset': 0,
            'limit': 5,
        }
        
        response = requests.get(BASE_URL, params=params)
        print(f"API Response Status Code: {response.status_code}")
        
        data = response.json()
        
        if isinstance(data, list):
            return data
        else:
            print(f"Error fetching news: {data.get('message', 'Unknown error')}")
            return []
            
    except Exception as e:
        print(f"Error fetching news: {str(e)}")
        return []
