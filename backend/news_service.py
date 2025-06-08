from sqlalchemy.orm import Session
from config import SessionLocal
import models
from marketaux_config import get_apple_news

def update_news():
    """Fetch and update news about Apple."""
    db = SessionLocal()
    try:
        news_items = get_apple_news()
        
        for item in news_items:
            # Create new news record
            news_record = models.News(
                title=item['title'],
                description=item.get('description', ''),
                url=item['url'],
                sentiment=item.get('sentiment', 'neutral')
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
        .limit(2)\
        .all()
    
    return [{
        'title': item.title,
        'description': item.description,
        'url': item.url,
        'sentiment': item.sentiment,
        'timestamp': item.timestamp.isoformat()
    } for item in news] 