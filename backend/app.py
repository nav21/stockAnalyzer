from flask import Flask, jsonify, request
from flask_cors import CORS
from sqlalchemy.orm import Session
from config import engine, get_db
import models
from openai_config import get_food_explanation
from stock_service import update_stock_prices, get_latest_prices
from news_service import update_news, get_latest_news
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = Flask(__name__)
CORS(app)

# Initialize scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(update_stock_prices, 'interval', minutes=120)
scheduler.add_job(update_news, 'interval', minutes=60)
scheduler.start()

@app.route('/api/foods', methods=['GET'])
def get_foods():
    db: Session = next(get_db())
    try:
        foods = db.query(models.Food).all()
        return jsonify([{"id": food.id, "name": food.name} for food in foods])
    finally:
        db.close()

@app.route('/api/foods', methods=['POST'])
def create_food():
    db: Session = next(get_db())
    try:
        food_data = request.get_json()
        if not food_data or 'name' not in food_data:
            return jsonify({"error": "Name is required"}), 400

        new_food = models.Food(name=food_data['name'])
        db.add(new_food)
        db.commit()
        db.refresh(new_food)
        return jsonify({"id": new_food.id, "name": new_food.name}), 201
    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()

@app.route('/api/foods/<int:food_id>/explanation', methods=['GET'])
def get_food_explanation_endpoint(food_id):
    db: Session = next(get_db())
    try:
        food = db.query(models.Food).filter(models.Food.id == food_id).first()
        if not food:
            return jsonify({"error": "Food not found"}), 404
        
        explanation = get_food_explanation(food.name)
        return jsonify({"explanation": explanation})
    finally:
        db.close()

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
        news = get_latest_news(db)
        return jsonify(news)
    finally:
        db.close()

if __name__ == '__main__':
    # Initial updates
    update_stock_prices()
    update_news()
    app.run(debug=True, port=5000)