import os
import google.generativeai as genai
from dotenv import load_dotenv
import json
from datetime import datetime
import pytz

load_dotenv()

genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
FALLBACK_TIMEZONE = pytz.timezone('America/New_York')

def _extract_date_range_from_question(question: str):
    try:
        prompt = f"""
        Analyze the following user question to extract a start date and an end date.
        
        Rules:
        - If the user asks for a specific date range (e.g., "fromRIBUTES-MM-DD toRIBUTES-MM-DD"), use those dates.
        - If the user asks for "last N days/weeks/months/years", calculate the start date relative to today's date.
        - If the user asks for a specific quarter (e.g., "Q1 2023", "Quarter 2 2024"), calculate the start and end dates for that quarter.
        - If the user asks for a specific year (e.g., "in 2023", "2022"), use January 1st and December 31st of that year.
        - If no clear date range is specified, or if the dates are in the future, return null for both start_date and end_date.
        - All dates must be inRIBUTES-MM-DD format.
        - Today's date is {datetime.now().strftime('%Y-%m-%d')}.
        
        User question: "{question}"
        """
        
        response_schema = {
            "type": "OBJECT",
            "properties": {
                "start_date": {"type": "STRING", "nullable": True, "description": "Start date inRIBUTES-MM-DD format, or null if not specified/invalid."},
                "end_date": {"type": "STRING", "nullable": True, "description": "End date inRIBUTES-MM-DD format, or null if not specified/invalid."}
            },
            "propertyOrdering": ["start_date", "end_date"]
        }

        model = genai.GenerativeModel('gemini-2.0-flash-lite', 
                                     generation_config={"response_mime_type": "application/json", 
                                                         "response_schema": response_schema})
        
        response = model.generate_content(prompt)
        
        date_info = json.loads(response.text)
        
        start_date = date_info.get('start_date')
        end_date = date_info.get('end_date')

        today = datetime.now().date()
        if start_date:
            try:
                parsed_start = datetime.strptime(start_date, '%Y-%m-%d').date()
                if parsed_start > today:
                    start_date = None
            except ValueError:
                start_date = None
        if end_date:
            try:
                parsed_end = datetime.strptime(end_date, '%Y-%m-%d').date()
                if parsed_end > today:
                    end_date = today.strftime('%Y-%m-%d')
            except ValueError:
                end_date = None

        return start_date, end_date

    except Exception as e:
        print(f"Error extracting date range with LLM: {e}")
        return None, None

def get_stock_analysis(question, stock_data, news_data, user_timezone_str: str = None):
    target_timezone = FALLBACK_TIMEZONE
    if user_timezone_str:
        try:
            target_timezone = pytz.timezone(user_timezone_str)
        except pytz.exceptions.UnknownTimeZoneError:
            print(f"Warning: Unknown timezone '{user_timezone_str}'. Falling back to {FALLBACK_TIMEZONE.tzname(datetime.now())}.")
    try:
        if not isinstance(stock_data, dict) or not stock_data:
            return "Error: Stock data is not in the expected dictionary format or is empty."

        symbol = list(stock_data.keys())[0]
        prices_list_raw = stock_data[symbol] 

        if not isinstance(prices_list_raw, list):
            return "Error: Price list for stock data is not a list."

        oldest_date_str = None
        newest_date_str = None

        stock_prices_detail = []
        for price_record_raw in prices_list_raw:
            price_record = price_record_raw 

            if isinstance(price_record_raw, str):
                try:
                    price_record = json.loads(price_record_raw.replace("'", "\""))
                except json.JSONDecodeError as e:
                    print(f"Warning: Could not decode price record string: '{price_record_raw}'. Error: {e}")
                    continue
            
            if not isinstance(price_record, dict) or 'price' not in price_record or 'timestamp' not in price_record:
                print(f"Warning: Unexpected format for price_record: {price_record}. Skipping.")
                continue

            try:
                current_timestamp = datetime.fromisoformat(price_record['timestamp'])
                formatted_timestamp = current_timestamp.strftime('%Y-%m-%d %I:%M:%S %p')
                current_date_str = current_timestamp.strftime('%Y-%m-%d')
                
                if oldest_date_str is None or current_date_str < oldest_date_str:
                    oldest_date_str = current_date_str
                if newest_date_str is None or current_date_str > newest_date_str:
                    newest_date_str = current_date_str

                stock_prices_detail.append(f"  Price: ${price_record['price']:.2f} (As of: {formatted_timestamp})")
            except ValueError:
                stock_prices_detail.append(f"  Price: ${price_record.get('price', 'N/A'):.2f} (As of: Invalid Date)")

        stock_prices_context = f"Symbol: {symbol}\n"
        if oldest_date_str and newest_date_str and oldest_date_str != newest_date_str:
            stock_prices_context += f"Stock Price History (spanning from {oldest_date_str} to {newest_date_str}):\n"
        elif oldest_date_str:
            stock_prices_context += f"Stock Price History (all data from {oldest_date_str}):\n"
        else:
            stock_prices_context += "Stock Price History:\n"

        stock_prices_context += "\n".join(stock_prices_detail)


        context = f"""
        {stock_prices_context}

        Recent News:
        {format_news_for_context(news_data)}

        Question: {question}
        """

        model = genai.GenerativeModel('gemini-2.0-flash-lite')
        
        response = model.generate_content(
            f"""You are a financial analyst assistant. Based on the provided stock price history and recent news, 
            answer the following question about {symbol}'s stock price movement. 
            Be concise and focus on the most relevant information.
            
            Context:
            {context}
            """
        )
        
        return response.text
    except Exception as e:
        import traceback
        traceback.print_exc() 
        return f"Error getting analysis: {str(e)}"

def format_news_for_context(news_data):
    formatted_news = []
    for article in news_data:
        formatted_news.append(f"""
        Title: {article['title']}
        Content: {article['content']}
        Published: {article['timestamp']}
        """)
    return "\n".join(formatted_news)
