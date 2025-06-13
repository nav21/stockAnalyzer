from sqlalchemy.orm import Session
from config import SessionLocal
import models
from eodhd_price_config import get_stock_price

STOCK_SYMBOLS = ['AAPL', 'AMZN', 'GOOGL', 'MSFT', 'TSLA']
#STOCK_SYMBOLS = ['AAPL']

def update_stock_prices():
    """Fetch and update stock prices for all tracked symbols."""
    db = SessionLocal()
    try:
        for symbol in STOCK_SYMBOLS:
            try:
                # Fetch the latest price from Alpha Vantage
                # It's crucial that get_stock_price returns None or 0 or
                # raises an exception if fetching fails or returns invalid data.
                price = get_stock_price(symbol)
                
                # IMPORTANT: Only add the record if 'price' is a valid number (float/int)
                # and is not None or zero (unless zero is a valid price).
                if isinstance(price, (float, int)) and price > 0: # Ensure price is a positive number
                    # Create new stock price record
                    stock_record = models.Stock(
                        symbol=symbol,
                        price=price
                    )
                    db.add(stock_record)
                    print(f"Successfully added price for {symbol}: {price}")
                else:
                    print(f"Skipping update for {symbol}: Invalid or no price received ({price}). Check API key/call.")
            except Exception as e:
                print(f"Error fetching or processing price for {symbol}: {str(e)}")
        
        db.commit()
    except Exception as e:
        print(f"Error updating stock prices batch: {str(e)}")
        db.rollback()
    finally:
        db.close()

def get_latest_prices(db: Session, symbol: str = None):
    """Get the latest price for each stock symbol."""

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
    """Get the latest price for each stock symbol."""
    all_latest_ten_prices = {}
    
    # Ensure only one symbol is processed: either the provided one or 'AAPL'
    target_symbol = (symbol.upper() if symbol else 'AAPL') 

    # Simplified query to get the latest 10 records
    stocks = db.query(models.Stock)\
        .filter(models.Stock.symbol == target_symbol)\
        .order_by(models.Stock.timestamp.desc())\
        .limit(10)\
        .all()

    symbol_prices = []
    for stock in stocks:
        symbol_prices.append({
            'price': stock.price,
            'timestamp': stock.timestamp.isoformat()
        })
    all_latest_ten_prices[target_symbol] = symbol_prices
            
    return all_latest_ten_prices