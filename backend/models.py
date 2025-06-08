from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from config import Base
from datetime import datetime

class Food(Base):
    __tablename__ = "foods"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)

class Stock(Base):
    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    price = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)

class News(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(Text)
    url = Column(String)
    sentiment = Column(String)  # positive, negative, or neutral
    timestamp = Column(DateTime, default=datetime.utcnow) 