import os
import google.generativeai as genai
from dotenv import load_dotenv
import json
from datetime import datetime

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

def get_stock_analysis(question, stock_data, news_data):
    """
    Get analysis from Gemini based on the question and available data.
    
    Args:
        question (str): User's question about the stock
        stock_data (dict): A dictionary where keys are stock symbols
                           and values are lists of the latest 10+ price records.
                           Example: {'AAPL': [{'price': 170.0, 'timestamp': '2025-06-09T10:00:00'}, ...]}
        news_data (list): List of recent news articles
    
    Returns:
        str: Gemini's analysis response
    """
    try:
        if not isinstance(stock_data, dict) or not stock_data:
            return "Error: Stock data is not in the expected dictionary format or is empty."

        symbol = list(stock_data.keys())[0]
        prices_list_raw = stock_data[symbol] 

        if not isinstance(prices_list_raw, list):
            return "Error: Price list for stock data is not a list."

        # Initialize dates for range tracking
        oldest_date_str = None
        newest_date_str = None

        # Prepare detailed price history context
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
                formatted_timestamp = current_timestamp.strftime('%Y-%m-%d %H:%M:%S')
                current_date_str = current_timestamp.strftime('%Y-%m-%d')
                
                # Update oldest and newest dates
                if oldest_date_str is None or current_date_str < oldest_date_str:
                    oldest_date_str = current_date_str
                if newest_date_str is None or current_date_str > newest_date_str:
                    newest_date_str = current_date_str

                stock_prices_detail.append(f"  Price: ${price_record['price']:.2f} (As of: {formatted_timestamp})")
            except ValueError:
                stock_prices_detail.append(f"  Price: ${price_record.get('price', 'N/A'):.2f} (As of: Invalid Date)")

        # Construct the stock prices context with the explicit date range summary at the top
        stock_prices_context = f"Symbol: {symbol}\n"
        if oldest_date_str and newest_date_str and oldest_date_str != newest_date_str:
            stock_prices_context += f"Stock Price History (spanning from {oldest_date_str} to {newest_date_str}):\n"
        elif oldest_date_str:
            stock_prices_context += f"Stock Price History (all data from {oldest_date_str}):\n"
        else:
            stock_prices_context += "Stock Price History:\n"

        stock_prices_context += "\n".join(stock_prices_detail)


        # Format the overall context for Gemini
        context = f"""
        {stock_prices_context}

        Recent News:
        {format_news_for_context(news_data)}

        Question: {question}
        """

        # Initialize the model
        model = genai.GenerativeModel('gemini-1.5-flash-8b')
        
        # Generate response
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
    """Format news data for the context string."""
    formatted_news = []
    for article in news_data:
        formatted_news.append(f"""
        Title: {article['title']}
        Content: {article['content']}
        Published: {article['timestamp']}
        """)
    return "\n".join(formatted_news)
