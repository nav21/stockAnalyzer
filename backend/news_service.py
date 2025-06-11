from sqlalchemy.orm import Session
from config import SessionLocal
import models
from eodhd_config import get_apple_news
from datetime import datetime
from sqlalchemy.exc import IntegrityError

def update_news():
    """Fetch and update news about Apple."""
    db = SessionLocal()
    try:
        news_items = get_apple_news()
        added_count = 0
        duplicate_count = 0
        
        for item in news_items:
            try:
                # Check if news with this title already exists
                existing_news = db.query(models.News).filter(
                    models.News.title == item['title']
                ).first()
                
                if existing_news:
                    duplicate_count += 1
                    continue
                
                # Create new news record
                news_record = models.News(
                    title=item['title'],
                    content=item.get('content', ''),
                    url=item['link'],
                    timestamp=datetime.fromisoformat(item['date'])
                )
                db.add(news_record)
                added_count += 1
                
            except IntegrityError:
                # Handle case where unique constraint is violated
                db.rollback()
                duplicate_count += 1
                continue
            except Exception as e:
                print(f"Error processing news item: {str(e)}")
                continue
        
        db.commit()
        print(f"News update complete. Added: {added_count}, Duplicates skipped: {duplicate_count}")
    except Exception as e:
        print(f"Error updating news: {str(e)}")
        db.rollback()
    finally:
        db.close()

def get_latest_news(db: Session):
    """Get the latest news items."""
    news = db.query(models.News)\
        .order_by(models.News.timestamp.desc())\
        .limit(5)\
        .all()
    
    return [{
        'title': item.title,
        'content': item.content,
        'url': item.url,
        'timestamp': item.timestamp.isoformat()
    } for item in news] 