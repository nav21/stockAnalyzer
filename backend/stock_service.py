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
                price = get_stock_price(symbol)
                
                if price:
                    # Create new stock price record
                    stock_record = models.Stock(
                        symbol=symbol,
                        price=price
                    )
                    db.add(stock_record)
            except Exception as e:
                print(f"Error fetching price for {symbol}: {str(e)}")
        
        db.commit()
    except Exception as e:
        print(f"Error updating stock prices: {str(e)}")
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