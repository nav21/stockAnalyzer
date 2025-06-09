from sqlalchemy.orm import Session
from config import SessionLocal
import models
from eodhd_config import get_apple_news
from datetime import datetime

def update_news():
    """Fetch and update news about Apple."""
    db = SessionLocal()
    try:
        news_items = get_apple_news()
        
        for item in news_items:
            # Create new news record
            news_record = models.News(
                title=item['title'],
                content=item.get('content', ''),
                url=item['link'],
                timestamp=datetime.fromisoformat(item['date'])
            )
            db.add(news_record)
        
        db.commit()
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