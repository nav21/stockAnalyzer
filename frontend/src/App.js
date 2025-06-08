import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [foods, setFoods] = useState([]);
  const [newFood, setNewFood] = useState('');
  const [selectedFood, setSelectedFood] = useState(null);
  const [explanation, setExplanation] = useState('');
  const [loading, setLoading] = useState(false);
  const [stocks, setStocks] = useState({});
  const [news, setNews] = useState([]);

  useEffect(() => {
    fetchFoods();
    fetchStocks();
    fetchNews();
    // Set up intervals
    const stockInterval = setInterval(fetchStocks, 60000);
    const newsInterval = setInterval(fetchNews, 60000);
    return () => {
      clearInterval(stockInterval);
      clearInterval(newsInterval);
    };
  }, []);

  const fetchFoods = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/foods');
      setFoods(response.data);
    } catch (error) {
      console.error('Error fetching foods:', error);
    }
  };

  const fetchStocks = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/stocks');
      setStocks(response.data);
    } catch (error) {
      console.error('Error fetching stocks:', error);
    }
  };

  const fetchNews = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/news');
      setNews(response.data);
    } catch (error) {
      console.error('Error fetching news:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post('http://localhost:5000/api/foods', { name: newFood });
      setNewFood('');
      fetchFoods();
    } catch (error) {
      console.error('Error adding food:', error);
    }
  };

  const handleFoodClick = async (food) => {
    setSelectedFood(food);
    setLoading(true);
    try {
      const response = await axios.get(`http://localhost:5000/api/foods/${food.id}/explanation`);
      setExplanation(response.data.explanation);
    } catch (error) {
      console.error('Error fetching explanation:', error);
      setExplanation('Error getting explanation');
    } finally {
      setLoading(false);
    }
  };

  const formatPrice = (price) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(price);
  };

  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  const getSentimentColor = (sentiment) => {
    switch (sentiment.toLowerCase()) {
      case 'positive':
        return '#4caf50';
      case 'negative':
        return '#f44336';
      default:
        return '#9e9e9e';
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Food List & Stock Prices</h1>
        
        <div className="stocks-container">
          <h2>Stock Prices</h2>
          <div className="stocks-grid">
            {Object.entries(stocks).map(([symbol, data]) => (
              <div key={symbol} className="stock-card">
                <h3>{symbol}</h3>
                <div className="stock-price">{formatPrice(data.price)}</div>
                <div className="stock-time">Updated: {formatTime(data.timestamp)}</div>
              </div>
            ))}
          </div>
        </div>

        <div className="news-container">
          <h2>Latest Apple News</h2>
          <div className="news-list">
            {news.map((item, index) => (
              <div key={index} className="news-card">
                <h3>{item.title}</h3>
                <p>{item.description}</p>
                <div className="news-footer">
                  <span 
                    className="sentiment-badge"
                    style={{ backgroundColor: getSentimentColor(item.sentiment) }}
                  >
                    {item.sentiment}
                  </span>
                  <a 
                    href={item.url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="read-more"
                  >
                    Read More
                  </a>
                </div>
              </div>
            ))}
          </div>
        </div>

        <form onSubmit={handleSubmit} className="food-form">
          <input
            type="text"
            value={newFood}
            onChange={(e) => setNewFood(e.target.value)}
            placeholder="Enter food name"
            className="food-input"
          />
          <button type="submit" className="add-button">Add Food</button>
        </form>

        <div className="content-container">
          <div className="food-list">
            {foods.map((food) => (
              <div
                key={food.id}
                className={`food-item ${selectedFood?.id === food.id ? 'selected' : ''}`}
                onClick={() => handleFoodClick(food)}
              >
                {food.name}
              </div>
            ))}
          </div>

          {selectedFood && (
            <div className="explanation-container">
              <h2>{selectedFood.name}</h2>
              {loading ? (
                <div className="loading">Loading explanation...</div>
              ) : (
                <p className="explanation">{explanation}</p>
              )}
            </div>
          )}
        </div>
      </header>
    </div>
  );
}

export default App; 