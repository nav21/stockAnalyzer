from sqlalchemy.orm import Session
from config import SessionLocal
import models
from eodhd_price_config import get_stock_price, get_eodhd_historical_data
from sqlalchemy.exc import IntegrityError 
from sqlalchemy import Date 
import pytz 
from datetime import datetime 

STOCK_SYMBOLS = ['AAPL', 'AMZN', 'GOOGL', 'MSFT', 'TSLA']
#STOCK_SYMBOLS = ['AAPL']

def is_market_open():
    eastern = pytz.timezone('America/New_York')
    
    now_et = datetime.now(eastern)
    
    day_of_week = now_et.weekday()
    
    market_open_time = now_et.replace(hour=9, minute=30, second=0, microsecond=0)
    market_close_time = now_et.replace(hour=16, minute=0, second=0, microsecond=0)

    if 0 <= day_of_week <= 4: 
        if market_open_time <= now_et <= market_close_time:
            print(f"DEBUG: Market is OPEN. Current ET time: {now_et.strftime('%H:%M:%S')}")
            return True
        else:
            print(f"DEBUG: Market is CLOSED (outside hours). Current ET time: {now_et.strftime('%H:%M:%S')}")
            return False
    else:
        print(f"DEBUG: Market is CLOSED (weekend). Current ET time: {now_et.strftime('%Y-%m-%d %H:%M:%S')}, Day: {now_et.strftime('%A')}")
        return False


def update_stock_prices():

    if not is_market_open():
        print("Market is currently closed. Skipping real-time stock price update.")
        return 
    
    db = SessionLocal()
    try:
        for symbol in STOCK_SYMBOLS:
            try:
                stock_data = get_stock_price(symbol)
                
               
                if stock_data and isinstance(stock_data, dict) and \
                    isinstance(stock_data.get('price'), (float, int)) and \
                    stock_data['price'] > 0 and stock_data.get('timestamp'): 
                    stock_record = models.Stock(
                        symbol=symbol,
                        price=stock_data['price'],
                        timestamp=stock_data['timestamp']
                    )
                    db.add(stock_record)
                    print(f"Successfully added price for {symbol}: {stock_data['price']} at {stock_data['timestamp']}")
                else:
                    print(f"Skipping update for {symbol}: Invalid or incomplete data received ({stock_data}).")
            except Exception as e:
                print(f"Error fetching or processing price for {symbol}: {str(e)}")
        
        db.commit()
    except Exception as e:
        print(f"Error updating stock prices batch: {str(e)}")
        db.rollback()
    finally:
        db.close()

def get_latest_prices(db: Session, symbol: str = None):

    target_symbol = (symbol.upper() if symbol else 'AAPL') 

    latest_prices = {}
    stock = db.query(models.Stock)\
        .filter(models.Stock.symbol == target_symbol)\
        .order_by(models.Stock.timestamp.desc())\
        .first()
    if stock:
        latest_prices[target_symbol] = {
            'price': stock.price,
            'timestamp': stock.timestamp.isoformat()
            }
    return latest_prices 

def get_latest_ten_prices(db: Session, symbol: str = None):
    all_latest_ten_prices = {}
    
    target_symbol = (symbol.upper() if symbol else 'AAPL') 

    stocks = db.query(models.Stock)\
        .filter(models.Stock.symbol == target_symbol)\
        .order_by(models.Stock.timestamp.desc())\
        .limit(500)\
        .all()

    symbol_prices = []
    for stock in stocks:
        symbol_prices.append({
            'price': stock.price,
            'timestamp': stock.timestamp.isoformat()
        })
    all_latest_ten_prices[target_symbol] = symbol_prices
            
    return all_latest_ten_prices



def populate_historical_stock_data(start_date: str, end_date: str):
   
    db = SessionLocal()
    total_added_count = 0
    try:
        for symbol in STOCK_SYMBOLS:
            print(f"Attempting to fetch and populate historical data for {symbol} from {start_date} to {end_date}...")
            historical_data = get_eodhd_historical_data(symbol, start_date, end_date)
            
            if not historical_data:
                print(f"No historical data fetched for {symbol} in the specified range. Skipping.")
                continue

            added_count_for_symbol = 0
            for entry in historical_data:
                try:
                    existing_record = db.query(models.Stock).filter(
                        models.Stock.symbol == symbol,
                        models.Stock.timestamp.cast(Date) == entry['date'].date() 
                    ).first()

                    if existing_record:
                        continue

                    stock_record = models.Stock(
                        symbol=symbol,
                        price=entry['close'],
                        timestamp=entry['date'] 
                    )
                    db.add(stock_record)
                    added_count_for_symbol += 1
                except IntegrityError: 
                    db.rollback() 
                    print(f"Integrity error for {symbol} on {entry['date']}. Rolling back current item.")
                    continue
                except Exception as e:
                    print(f"Error processing historical entry for {symbol} on {entry['date']}: {str(e)}")
                    continue
            
            db.commit() 
            total_added_count += added_count_for_symbol
            print(f"Successfully added {added_count_for_symbol} historical records for {symbol}.")

    except Exception as e:
        print(f"Error populating historical stock data batch: {str(e)}")
        db.rollback()
    finally:
        db.close()
