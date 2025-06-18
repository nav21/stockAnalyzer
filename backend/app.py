from flask import Flask, jsonify, request
from flask_cors import CORS
from sqlalchemy.orm import Session
from config import engine, get_db
import models
from stock_service import update_stock_prices, get_latest_prices, populate_historical_stock_data, get_latest_ten_prices
from news_service import update_news, get_news_in_range, get_latest_news
from gemini_config import get_stock_analysis, _extract_date_range_from_question
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import os

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = Flask(__name__)
CORS(app)

scheduler = BackgroundScheduler()
scheduler.add_job(update_stock_prices, 'interval', minutes=300)
scheduler.add_job(update_news, 'interval', minutes=600)
scheduler.start()

@app.route('/api/stocks', methods=['GET'])
def get_stocks():
    db: Session = next(get_db())
    try:
        symbol = request.args.get('symbol')
        
        latest_prices = get_latest_prices(db, symbol=symbol) 
        return jsonify(latest_prices)
    finally:
        db.close()

@app.route('/api/news', methods=['GET'])
def get_news():
    db: Session = next(get_db())
    try:
        symbol = request.args.get('symbol') 
        print(f"DEBUG: app.py - Received symbol in /api/news: '{symbol}' (Type: {type(symbol)})")
        news = get_latest_news(db, symbol=symbol)
       
        return jsonify(news)
    finally:
        db.close()

@app.route('/api/analyze', methods=['POST'])
def analyze_stock():
    db: Session = next(get_db())
    try:
        question = request.json.get('question')
        selected_symbol_for_analysis = request.json.get('selectedSymbol') 
        user_timezone = request.json.get('userTimezone')

        if not question:
            return jsonify({"error": "Question is required"}), 400
        
        start_date, end_date = _extract_date_range_from_question(question)


        stock_data = get_latest_ten_prices(db, symbol=selected_symbol_for_analysis)
        news_data = get_news_in_range(db, symbol=selected_symbol_for_analysis, 
                                       from_date=start_date, to_date=end_date) 
        
        print(f"DEBUG: app.py - Before get_stock_analysis: selected_symbol={selected_symbol_for_analysis}")
        print(f"DEBUG: app.py - Before get_stock_analysis: stock_data={stock_data}")
        print(f"DEBUG: app.py - Before get_stock_analysis: news_data count={len(news_data)}")

        analysis = get_stock_analysis(question, stock_data, news_data, user_timezone) # <--- PASS USER'S TIMEZONE
        return jsonify({"analysis": analysis})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()

@app.route('/api/populate-historical', methods=['POST'])

def populate_historical():
  
    data = request.get_json()
    start_date = data.get('start_date')
    end_date = data.get('end_date')

    if not all([start_date, end_date]):
        return jsonify({"error": "start_date and end_date are required"}), 400
    

    try:
        populate_historical_stock_data(start_date, end_date)
        return jsonify({"message": f"Historical data population started for {start_date} to {end_date}."}), 200
    except Exception as e:
        print(f"Error in /api/populate-historical: {str(e)}")
        return jsonify({"error": f"Failed to populate historical data: {str(e)}"}), 500


if __name__ == '__main__':
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        print("Running initial data updates (only once)...")
        update_stock_prices() 
        update_news()
    app.run(debug=True, port=5000)