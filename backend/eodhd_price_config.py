import os
import requests
from dotenv import load_dotenv
from datetime import datetime
import pytz

load_dotenv()

EODHD_API_KEY = os.getenv('EODHD_API_KEY')
BASE_URL = 'https://eodhd.com/api/real-time/'
EODHD_HISTORICAL_BASE_URL = 'https://eodhd.com/api/eod/' 


def get_stock_price(symbol):
    if not EODHD_API_KEY:
        print("Error: EODHD_API_KEY not found in environment variables.")
        return None

    full_symbol = f"{symbol.upper()}.US" 

    try:
        params = {
            'api_token': EODHD_API_KEY,
            'fmt': 'json', 
        }
        
        response = requests.get(f"{BASE_URL}{full_symbol}", params=params)

        print(f"DEBUG: EODHD Real-Time Response Status Code for {full_symbol}: {response.status_code}")
        print(f"DEBUG: EODHD Real-Time Raw Response Text for {full_symbol}: {response.text}")

        if response.status_code != 200:
            print(f"Error fetching price for {full_symbol}: HTTP Status {response.status_code}. Response: {response.text}")
            return None

        data = response.json()
        
        print(f"DEBUG: EODHD Real-Time Parsed JSON Data for {full_symbol}: {data}")
        
        if isinstance(data, dict) and 'close' in data and 'timestamp' in data:
            price = float(data['close'])
            unix_timestamp = int(data['timestamp'])
            timestamp_dt = datetime.fromtimestamp(unix_timestamp, tz=pytz.utc)

            print(f"Successfully fetched price for {full_symbol}: {price} at {timestamp_dt}")
            return {'price': price, 'timestamp': timestamp_dt}
        else:
            print(f"Error fetching price for {full_symbol}: Unexpected data format or missing 'close'/'timestamp'. Data: {data}")
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
    
def get_eodhd_historical_data(symbol: str, start_date: str, end_date: str):
    
    if not EODHD_API_KEY:
        print("Error: EODHD_API_KEY not found in environment variables.")
        return []

    full_symbol = f"{symbol.upper()}.US" 

    try:
        params = {
            'api_token': EODHD_API_KEY,
            'fmt': 'json',
            'from': start_date,
            'to': end_date
        }
        
        response = requests.get(f"{EODHD_HISTORICAL_BASE_URL}{full_symbol}", params=params)

        print(f"DEBUG: EODHD Historical Response Status Code for {full_symbol} ({start_date} to {end_date}): {response.status_code}")

        if response.status_code != 200:
            print(f"Error fetching historical data for {full_symbol}: HTTP Status {response.status_code}. Response: {response.text}")
            return []

        data = response.json()
        
        
        if isinstance(data, list):
            historical_records = []
            for item in data:
                if 'date' in item and 'close' in item:
                    try:
                        record_date = datetime.strptime(item['date'], '%Y-%m-%d')
                        historical_records.append({
                            'date': record_date,
                            'close': float(item['close'])
                        })
                    except (ValueError, TypeError) as e:
                        print(f"Warning: Could not parse date or price for historical record: {item}. Error: {e}")
            return historical_records
        else:
            print(f"Error fetching historical data for {full_symbol}: API returned non-list data or error. Data: {data}")
            return []
            
    except requests.exceptions.RequestException as req_err:
        print(f"Network or request error fetching historical data for {full_symbol}: {req_err}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred fetching historical data for {full_symbol}: {str(e)}")
        return []
