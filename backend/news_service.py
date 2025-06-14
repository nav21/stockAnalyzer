from sqlalchemy.orm import Session
from config import SessionLocal
import models
from eodhd_config import get_news
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from datetime import datetime

NEWS_SYMBOLS = ['AAPL', 'AMZN', 'GOOGL', 'MSFT', 'TSLA'] 
def update_news():
   
    db = SessionLocal()
    total_added_count = 0
    total_duplicate_count = 0
    
    to_date = '2025-06-13'
    from_date = '2025-06-05'


    try:
        for symbol in NEWS_SYMBOLS:
            print(f"Attempting to fetch and update news for {symbol}...")
            try:
                news_items = get_news(symbol, from_date=from_date, to_date=to_date) 
                
                if not news_items:
                    print(f"No news fetched for {symbol}. Skipping database update for this symbol.")
                    continue 

                added_count_for_symbol = 0
                duplicate_count_for_symbol = 0

                for item in news_items:
                    try:
                        extracted_symbols = item.get('symbols', [])
                        print(f"DEBUG: Processing news item for '{symbol}'. Article Title: '{item.get('title', 'N/A')}', Date: '{item.get('date', 'N/A')}', Extracted Symbols: {extracted_symbols}")
                
                        existing_news = db.query(models.News).filter(
                            models.News.title == item.get('title') 
                        ).first()
                        
                        if existing_news:
                            duplicate_count_for_symbol += 1
                            continue 
                        
                        news_record = models.News(
                            title=item.get('title', 'No Title'),
                            content=item.get('content', ''), 
                            url=item.get('link', ''),
                            timestamp=datetime.fromisoformat(item['date']) ,
                            symbols=item.get('symbols', []) 
                        )
                        db.add(news_record)
                        added_count_for_symbol += 1
                        
                    except IntegrityError:

                        db.rollback() 
                        print(f"Duplicate news title encountered (IntegrityError) for {item.get('title', 'N/A')}. Rolling back item add.")
                        duplicate_count_for_symbol += 1
                       
                        continue 
                    except KeyError as ke:
                        print(f"Error processing news item for {symbol}: Missing key - {ke}. Item: {item}. Skipping.")
                        continue 
                    except ValueError as ve: 
                        print(f"Error processing news item for {symbol}: Invalid timestamp format - {ve}. Item: {item.get('date', 'N/A')}. Skipping.")
                        continue
                    except Exception as e:
                        print(f"Generic error processing news item for {symbol}: {str(e)}. Item: {item}. Skipping.")
                        continue

                db.commit() 
                total_added_count += added_count_for_symbol
                total_duplicate_count += duplicate_count_for_symbol
                print(f"News update for {symbol} complete. Added: {added_count_for_symbol}, Duplicates skipped: {duplicate_count_for_symbol}")
            
            except Exception as e:
                print(f"Error during overall fetch/update for {symbol}: {str(e)}")
                
                db.rollback() 
                continue 

    except Exception as e:
        print(f"Critical error during news update process: {str(e)}")
        db.rollback()
    finally:
        db.close()
def get_news_in_range(db: Session, symbol: str = None, from_date: str = None, to_date: str = None):
  
    query = db.query(models.News)

    if symbol:
        symbol_for_query = symbol.upper()
        if not symbol_for_query.endswith('.US'):
            symbol_for_query = f"{symbol_for_query}.US"
        query = query.filter(models.News.symbols.any(symbol_for_query))

    if from_date and to_date:
        try:
            from_datetime = datetime.strptime(from_date, '%Y-%m-%d')
            to_datetime = datetime.strptime(to_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59, microsecond=999999)
            query = query.filter(models.News.timestamp.between(from_datetime, to_datetime))
        except ValueError:
            print(f"Warning: Invalid date format provided for news: {from_date} or {to_date}. Ignoring date filter and defaulting to latest 5.")
            query = query.order_by(models.News.timestamp.desc()).limit(5)
    else:
        query = query.order_by(models.News.timestamp.desc()).limit(5)


    news = query.all()
    
    return [{
        'title': item.title,
        'content': item.content, 
        'url': item.url,
        'timestamp': item.timestamp.isoformat(),
        'symbols': item.symbols 
    } for item in news]

def get_latest_news(db: Session, symbol: str):
    query = db.query(models.News) 

    if symbol:
        symbol_for_query = symbol.upper()
        if not symbol_for_query.endswith('.US'):
            symbol_for_query = f"{symbol_for_query}.US"
        query = query.filter(models.News.symbols.any(symbol_for_query))


    news = query.order_by(models.News.timestamp.desc())\
                .limit(5)\
                .all()
    
    return [{
        'title': item.title,
        'content': item.content,
        'url': item.url,
        'timestamp': item.timestamp.isoformat(),
        'symbols': item.symbols 
    } for item in news] 