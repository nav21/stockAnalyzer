import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [stocks, setStocks] = useState({});
  const [news, setNews] = useState([]);
  const [question, setQuestion] = useState('');
  const [analysis, setAnalysis] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  useEffect(() => {
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

  const handleQuestionSubmit = async (e) => {
    e.preventDefault();
    if (!question.trim()) return;

    setIsAnalyzing(true);
    try {
      const response = await axios.post('http://localhost:5000/api/analyze', {
        question: question
      });
      setAnalysis(response.data.analysis);
    } catch (error) {
      console.error('Error getting analysis:', error);
      setAnalysis('Error getting analysis. Please try again.');
    } finally {
      setIsAnalyzing(false);
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

  return (
    <div className="App">
      <header className="App-header">
        <h1>Stock Prices & News</h1>
        
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
                <p>{item.content}</p>
                <div className="news-footer">
                  <a
                    href={item.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="read-more"
                  >
                    Read More
                  </a>
                  <span className="news-timestamp">
                    {item.timestamp ? new Date(item.timestamp).toLocaleString() : 'N/A'}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="analysis-container">
          <h2>Ask About Apple's Stock</h2>
          <form onSubmit={handleQuestionSubmit} className="question-form">
            <input
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Ask about Apple's stock price movement..."
              className="question-input"
            />
            <button type="submit" className="analyze-button" disabled={isAnalyzing}>
              {isAnalyzing ? 'Analyzing...' : 'Analyze'}
            </button>
          </form>
          {analysis && (
            <div className="analysis-result">
              <h3>Analysis</h3>
              <p>{analysis}</p>
            </div>
          )}
        </div>
      </header>
    </div>
  );
}

export default App; 