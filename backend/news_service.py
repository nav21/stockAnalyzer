from sqlalchemy.orm import Session
from config import SessionLocal
import models
from eodhd_config import get_news
from datetime import datetime
from sqlalchemy.exc import IntegrityError
NEWS_SYMBOLS = ['AAPL', 'AMZN', 'GOOGL', 'MSFT', 'TSLA'] # Example: Update news for Apple, Google, Microsoft

def update_news():
    """
    Fetch and update news for all tracked stock symbols in NEWS_SYMBOLS.
    Includes duplicate checking based on news title.
    """
    db = SessionLocal()
    total_added_count = 0
    total_duplicate_count = 0
    
    try:
        for symbol in NEWS_SYMBOLS: # Loop through each symbol
            print(f"Attempting to fetch and update news for {symbol}...")
            try:
                # Pass the current symbol to the news fetching function
                news_items = get_news(symbol) 
                
                if not news_items:
                    print(f"No news fetched for {symbol}. Skipping database update for this symbol.")
                    continue # Move to the next symbol if no news

                added_count_for_symbol = 0
                duplicate_count_for_symbol = 0

                for item in news_items:
                    try:
                        extracted_symbols = item.get('symbols', [])
                        print(f"DEBUG: Processing news item for '{symbol}'. Article Title: '{item.get('title', 'N/A')}', Extracted Symbols: {extracted_symbols}")
                        # Check if news with this title already exists for the same symbol
                        # (Consider adding symbol to news model if you need news specific to symbol)
                        existing_news = db.query(models.News).filter(
                            models.News.title == item.get('title') # Use .get() for safety
                        ).first()
                        
                        if existing_news:
                            duplicate_count_for_symbol += 1
                            continue # Skip to next item if duplicate
                        
                        # Create new news record
                        news_record = models.News(
                            title=item.get('title', 'No Title'),
                            content=item.get('content', ''), 
                            url=item.get('link', ''),
                            timestamp=datetime.fromisoformat(item['date']) ,
                            symbols=item.get('symbols', []) # <--- IMPORTANT: Store the array
                        )
                        db.add(news_record)
                        added_count_for_symbol += 1
                        
                    except IntegrityError:
                        # This typically happens if you have a unique constraint on 'title'
                        db.rollback() # Rollback the current transaction for this item
                        print(f"Duplicate news title encountered (IntegrityError) for {item.get('title', 'N/A')}. Rolling back item add.")
                        duplicate_count_for_symbol += 1
                        # Re-establish a new transaction for subsequent items (if committing outside)
                        # If committing inside the loop, the transaction is implicitly new for next item
                        continue 
                    except KeyError as ke:
                        print(f"Error processing news item for {symbol}: Missing key - {ke}. Item: {item}. Skipping.")
                        continue # Skip to next item
                    except ValueError as ve: # Catching ValueError for fromisoformat
                        print(f"Error processing news item for {symbol}: Invalid timestamp format - {ve}. Item: {item.get('date', 'N/A')}. Skipping.")
                        continue # Skip to next item
                    except Exception as e:
                        print(f"Generic error processing news item for {symbol}: {str(e)}. Item: {item}. Skipping.")
                        continue

                db.commit() # Commit changes for the current symbol batch
                total_added_count += added_count_for_symbol
                total_duplicate_count += duplicate_count_for_symbol
                print(f"News update for {symbol} complete. Added: {added_count_for_symbol}, Duplicates skipped: {duplicate_count_for_symbol}")
            
            except Exception as e:
                print(f"Error during overall fetch/update for {symbol}: {str(e)}")
                # If an error prevents fetching all news for a symbol, rollback the session
                # and continue to the next symbol.
                db.rollback() 
                continue # Continue to the next symbol in NEWS_SYMBOLS

    except Exception as e:
        print(f"Critical error during news update process: {str(e)}")
        db.rollback() # Final rollback for any errors outside the inner loops
    finally:
        db.close()

def get_latest_news(db: Session, symbol: str):
    """Get the latest news items."""
    query = db.query(models.News) # <--- FIX: Initialize query with db.query()

    if symbol:
        symbol_for_query = symbol.upper()
        if not symbol_for_query.endswith('.US'):
            symbol_for_query = f"{symbol_for_query}.US"
        query = query.filter(models.News.symbols.any(symbol_for_query)) # <--- Changed line here


    news = query.order_by(models.News.timestamp.desc())\
                .limit(5)\
                .all()
    
    return [{
        'title': item.title,
        'content': item.content,
        'url': item.url,
        'timestamp': item.timestamp.isoformat(),
        'symbols': item.symbols # <--- Include the symbols array in output
    } for item in news] 