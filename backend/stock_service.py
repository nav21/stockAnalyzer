from sqlalchemy.orm import Session
from config import SessionLocal
import models
from alpha_vantage_config import get_stock_price

#STOCK_SYMBOLS = ['AAPL', 'AMZN', 'GOOGL', 'MSFT', 'TSLA']
STOCK_SYMBOLS = ['AAPL']

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

def get_latest_prices(db: Session):
    """Get the latest price for each stock symbol."""
    latest_prices = {}
    for symbol in STOCK_SYMBOLS:
        stock = db.query(models.Stock)\
            .filter(models.Stock.symbol == symbol)\
            .order_by(models.Stock.timestamp.desc())\
            .first()
        if stock:
            latest_prices[symbol] = {
                'price': stock.price,
                'timestamp': stock.timestamp.isoformat()
            }
    return latest_prices 

def get_latest_ten_prices(db: Session):
    """Get the latest price for each stock symbol."""
    latest_prices = {}
    for symbol in STOCK_SYMBOLS:
        # Query for the latest 10 stock records for the current symbol
        stocks = db.query(models.Stock)\
            .filter(models.Stock.symbol == symbol)\
            .order_by(models.Stock.timestamp.desc())\
            .limit(30)\
            .all() # Execute the query and get all 10 results

        # Initialize a list to store the formatted prices for the current symbol
        symbol_prices = []
        for stock in stocks:
            # Append each stock record as a dictionary to the list
            symbol_prices.append({
                'price': stock.price,
                'timestamp': stock.timestamp.isoformat()
            })
        
        # Assign the list of prices (symbol_prices) to the symbol in the latest_prices dictionary
        latest_prices[symbol] = symbol_prices
            
    return latest_prices