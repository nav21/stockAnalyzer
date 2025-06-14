import requests
import json

# Define the dates for historical data
start_date = "2025-03-13" # Change to your desired start date
end_date = "2025-06-13"   # Change to your desired end date

# Endpoint URL
url = "http://127.0.0.1:5000/api/populate-historical"

# JSON payload
payload = {
    "start_date": start_date,
    "end_date": end_date
}

print(f"Sending request to populate historical data from {start_date} to {end_date}...")

try:
    response = requests.post(url, json=payload) # Use json=payload to automatically set Content-Type

    response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)

    print("Response Status Code:", response.status_code)
    print("Response Body:", response.json())

except requests.exceptions.RequestException as e:
    print(f"Error sending request: {e}")
except json.JSONDecodeError:
    print(f"Error decoding JSON response. Raw response: {response.text}")