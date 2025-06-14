import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [stocks, setStocks] = useState({});
  const [news, setNews] = useState([]);

  const [questionsBySymbol, setQuestionsBySymbol] = useState(new Map());
  const [analysisBySymbol, setAnalysisBySymbol] = useState(new Map());

  const [currentQuestion, setCurrentQuestion] = useState('');
  const [currentAnalysis, setCurrentAnalysis] = useState('');

  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [showData, setShowData] = useState(false);
  // State for selected stock symbol
  const [selectedSymbol, setSelectedSymbol] = useState('AAPL.US'); 
  const [userTimezone, setUserTimezone] = useState(''); 


  useEffect(() => {
    setUserTimezone(Intl.DateTimeFormat().resolvedOptions().timeZone);

    fetchStocks(selectedSymbol); 
    fetchNews(selectedSymbol); 

    setCurrentQuestion(questionsBySymbol.get(selectedSymbol) || '');
    setCurrentAnalysis(analysisBySymbol.get(selectedSymbol) || '');

    const stockInterval = setInterval(fetchStocks(selectedSymbol), 720000);
    const newsInterval = setInterval(() => fetchNews(selectedSymbol), 720000); 
    return () => {
      clearInterval(stockInterval);
      clearInterval(newsInterval);
    };
  }, [selectedSymbol, questionsBySymbol, analysisBySymbol]); 

  const fetchStocks = async (symbol) => {
    try {
      const response = await axios.get(`http://localhost:5000/api/stocks?symbol=${symbol}`);
      setStocks(response.data); 
    } catch (error) {
      console.error('Error fetching stocks:', error);
      setStocks({}); 
    }
  };

  const fetchNews = async (symbol) => { 
    try {
      const response = await axios.get(`http://localhost:5000/api/news?symbol=${symbol}`); 
      setNews(response.data);
    } catch (error) {
      console.error('Error fetching news:', error);
    }
  };

  const handleQuestionSubmit = async (e) => {
    e.preventDefault();
    if (!currentQuestion.trim()) return;

    setIsAnalyzing(true);
    try {
      const response = await axios.post('http://localhost:5000/api/analyze', {
        question: currentQuestion,
        selectedSymbol: selectedSymbol, 
        userTimezone: userTimezone 
      });

      const newAnalysisResult = response.data.analysis;
      setCurrentAnalysis(newAnalysisResult); 

      setQuestionsBySymbol(prevMap => new Map(prevMap).set(selectedSymbol, currentQuestion));
      setAnalysisBySymbol(prevMap => new Map(prevMap).set(selectedSymbol, newAnalysisResult));

    } catch (error) {
      console.error('Error getting analysis:', error);
      setAnalysisBySymbol(prevMap => new Map(prevMap).set(selectedSymbol, 'Error getting analysis. Please try again.'));
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

  const handleSymbolChange = (event) => {
    const newSymbol = event.target.value;

    const oldSymbol = selectedSymbol;

    setQuestionsBySymbol(prevMap => new Map(prevMap).set(oldSymbol, currentQuestion));
    if (currentAnalysis) {
        setAnalysisBySymbol(prevMap => new Map(prevMap).set(oldSymbol, currentAnalysis));
    }
    
    setSelectedSymbol(newSymbol);

    fetchStocks(newSymbol); 
    fetchNews(newSymbol); 

    setCurrentQuestion(questionsBySymbol.get(newSymbol) || '');
    setCurrentAnalysis(analysisBySymbol.get(newSymbol) || '');
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1 className="app-title">Stockalyzer</h1> 
        
        <div className="header-controls"> 
          <select 
            className="stock-selector"
            value={selectedSymbol}
            onChange={handleSymbolChange}
          >
            <option value="AAPL">Apple</option>
            <option value="MSFT">Microsoft</option>
            <option value="TSLA">Tesla</option>
            <option value="AMZN">Amazon</option>
            <option value="GOOGL">Google</option>
          </select>
          <button 
            className="hollow-button" 
            onClick={() => setShowData(!showData)}
          >
            {showData ? 'Hide Data' : 'Show Data'}
          </button>
        </div>

        {showData && (
          <>
            <div className="stocks-container">
              <h2>Stock Price for {selectedSymbol}</h2>
              <div className="stocks-grid">
                {stocks[selectedSymbol] ? (
                  <div key={selectedSymbol} className="stock-card">
                    <h3>{selectedSymbol}</h3>
                    <div className="stock-price">{formatPrice(stocks[selectedSymbol].price)}</div>
                    <div className="stock-time">Updated: {formatTime(stocks[selectedSymbol].timestamp)}</div>
                  </div>
                ) : (
                  <p>Loading or no data for {selectedSymbol}</p>
                )}
              </div>
            </div>

            <div className="news-container">
              <h2>Latest News for {selectedSymbol}</h2> 
              <div className="news-list">
                {news.map((item, index) => (
                  <div key={index} className="news-card">
                    <h3>{item.title}</h3>
                    <div className="news-footer">
                      {item.symbols && Array.isArray(item.symbols) && item.symbols.length > 0 && (
                        <span className="news-symbols">
                          Symbols: {item.symbols.join(', ')}
                        </span>
                      )}
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
          </>
        )}

        <div className="analysis-container">
          <h2>Ask About {selectedSymbol}'s Stock</h2> 
          <form onSubmit={handleQuestionSubmit} className="question-form">
            <input
              type="text"
              value={currentQuestion}
              onChange={(e) => setCurrentQuestion(e.target.value)}
              placeholder={`Ask about ${selectedSymbol}'s stock price movement...`}
              className="question-input"
            />
            <button type="submit" className="analyze-button" disabled={isAnalyzing}>
              {isAnalyzing ? 'Analyzing...' : 'Analyze'}
            </button>
          </form>
          {currentAnalysis && (
            <div className="analysis-result">
              <h3>Analysis</h3>
              <p>{currentAnalysis}</p>
            </div>
          )}
        </div>
      </header>
    </div>
  );
}

export default App;
