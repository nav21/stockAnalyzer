from sqlalchemy import Column, Integer, String, Float, DateTime, Text, UniqueConstraint
from config import Base
from datetime import datetime
from sqlalchemy.dialects.postgresql import ARRAY # Import ARRAY for PostgreSQL array type


class Stock(Base):
    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    price = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)

class News(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, unique=True, index=True)
    content = Column(Text)
    url = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow) 
    symbols = Column(ARRAY(String), index=True) # Stores a list of symbols
