from flask import Flask, jsonify, request
from flask_cors import CORS
from sqlalchemy.orm import Session
from config import engine, get_db
import models
from stock_service import update_stock_prices, get_latest_prices, get_latest_ten_prices
from news_service import update_news, get_latest_news
from gemini_config import get_stock_analysis
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

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
        latest_prices = get_latest_prices(db)
        return jsonify(latest_prices)
    finally:
        db.close()

@app.route('/api/news', methods=['GET'])
def get_news():
    db: Session = next(get_db())
    try:
        symbol = request.args.get('symbol') 
        
        news = get_latest_news(db, symbol=symbol) 
        return jsonify(news)
    finally:
        db.close()

@app.route('/api/analyze', methods=['POST'])
def analyze_stock():
    db: Session = next(get_db())
    try:
        question = request.json.get('question')
        if not question:
            return jsonify({"error": "Question is required"}), 400

        # Get latest data
        stock_data = get_latest_ten_prices(db)
        news_data = get_latest_news(db)

        # Get analysis from Gemini
        analysis = get_stock_analysis(question, stock_data, news_data)
        return jsonify({"analysis": analysis})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()

if __name__ == '__main__':
    # Initial updates
    update_stock_prices()
    update_news()
    app.run(debug=True, port=5000)