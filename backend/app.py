from flask import Flask, jsonify, request
from flask_cors import CORS
from sqlalchemy.orm import Session
from config import engine, get_db
import models
from stock_service import update_stock_prices, get_latest_prices, populate_historical_stock_data, get_prices_in_range, get_latest_ten_prices
from news_service import update_news, get_news_in_range, get_latest_news
from gemini_config import get_stock_analysis, _extract_date_range_from_question
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import os

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = Flask(__name__)
CORS(app)

# Initialize scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(update_stock_prices, 'interval', minutes=300)
scheduler.add_job(update_news, 'interval', minutes=600)
scheduler.start()

@app.route('/api/stocks', methods=['GET'])
def get_stocks():
    db: Session = next(get_db())
    try:
        # Get the symbol from query parameters, if provided
        symbol = request.args.get('symbol')
        
        # Pass the symbol to get_latest_prices
        latest_prices = get_latest_prices(db, symbol=symbol) 
        return jsonify(latest_prices)
    finally:
        db.close()

@app.route('/api/news', methods=['GET'])
def get_news():
    db: Session = next(get_db())
    try:
        symbol = request.args.get('symbol') 
          # --- DEBUGGING PRINTS START ---
        print(f"DEBUG: app.py - Received symbol in /api/news: '{symbol}' (Type: {type(symbol)})")
        # --- DEBUGGING PRINTS END ---
        news = get_latest_news(db, symbol=symbol)
        # --- DEBUGGING PRINTS START ---
      #  print(f"DEBUG: app.py - News fetched from service (count: {len(news)}): {news[:1]}...") # Print first article to avoid too much output
        # --- DEBUGGING PRINTS END ---
        return jsonify(news)
    finally:
        db.close()

@app.route('/api/analyze', methods=['POST'])
def analyze_stock():
    db: Session = next(get_db())
    try:
        question = request.json.get('question')
        # We also need to get the selected symbol from the frontend for analysis context
        selected_symbol_for_analysis = request.json.get('selectedSymbol') 
        user_timezone = request.json.get('userTimezone')

        if not question:
            return jsonify({"error": "Question is required"}), 400
        
        start_date, end_date = _extract_date_range_from_question(question)


        stock_data = get_latest_ten_prices(db, symbol=selected_symbol_for_analysis)
        
        # Use the new get_news_in_range function, passing extracted dates
        # If dates are None, it will default to latest 5 as per news_service.py
        news_data = get_news_in_range(db, symbol=selected_symbol_for_analysis, 
                                       from_date=start_date, to_date=end_date) 
        
        print(f"DEBUG: app.py - Before get_stock_analysis: selected_symbol={selected_symbol_for_analysis}")
        print(f"DEBUG: app.py - Before get_stock_analysis: stock_data={stock_data}")
        print(f"DEBUG: app.py - Before get_stock_analysis: news_data count={len(news_data)}")
        # Get analysis from Gemini
        analysis = get_stock_analysis(question, stock_data, news_data, user_timezone) # <--- PASS USER'S TIMEZONE
        return jsonify({"analysis": analysis})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()

@app.route('/api/populate-historical', methods=['POST'])
def populate_historical():
    """
    Endpoint to manually trigger historical stock data population.
    Expects JSON body with 'start_date' and 'end_date'.
    Example: {"start_date": "2023-01-01", "end_date": "2023-12-31"}
    """
    data = request.get_json()
    start_date = data.get('start_date')
    end_date = data.get('end_date')

    if not all([start_date, end_date]):
        return jsonify({"error": "start_date and end_date are required"}), 400
    
    # You might want to add validation for date formats here

    try:
        populate_historical_stock_data(start_date, end_date)
        return jsonify({"message": f"Historical data population started for {start_date} to {end_date}."}), 200
    except Exception as e:
        print(f"Error in /api/populate-historical: {str(e)}")
        return jsonify({"error": f"Failed to populate historical data: {str(e)}"}), 500


if __name__ == '__main__':
    # Initial updates
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        print("Running initial data updates (only once)...")
        update_stock_prices() # Pass 'AAPL' for initial update
        update_news() # This will update news for all symbols in NEWS_SYMBOLS
    app.run(debug=True, port=5000)