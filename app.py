from flask import Flask, render_template, jsonify
from textblob import TextBlob
import requests
import os
from datetime import datetime
import pandas as pd

app = Flask(__name__)

# You would need to get an API key from a news service
NEWS_API_KEY = '42d887c3ac254d71b055ad4602a4a78d'
NEWS_API_ENDPOINT = 'https://newsapi.org/v2/everything'

def fetch_financial_news():
    """Fetch financial news articles from NewsAPI."""
    params = {
        'q': 'finance OR stock market OR economy',
        'apiKey': NEWS_API_KEY,
        'language': 'en',
        'sortBy': 'publishedAt',
        'pageSize': 10
    }
    
    try:
        response = requests.get(NEWS_API_ENDPOINT, params=params)
        response.raise_for_status()
        return response.json()['articles']
    except requests.exceptions.RequestException as e:
        print(f"Error fetching news: {e}")
        return []

def analyze_sentiment(text):
    """Analyze sentiment of text using TextBlob."""
    analysis = TextBlob(text)
    
    # Get polarity score (-1 to 1)
    polarity = analysis.sentiment.polarity
    
    # Determine sentiment category
    if polarity > 0.1:
        sentiment = "positive"
    elif polarity < -0.1:
        sentiment = "negative"
    else:
        sentiment = "neutral"
        
    return {
        'score': round(polarity, 2),
        'sentiment': sentiment
    }

def process_news_data(articles):
    """Process news articles and add sentiment analysis."""
    processed_articles = []
    
    for article in articles:
        # Combine title and description for better sentiment analysis
        text = f"{article['title']} {article['description']}"
        sentiment_data = analyze_sentiment(text)
        
        processed_articles.append({
            'title': article['title'],
            'description': article['description'],
            'url': article['url'],
            'publishedAt': article['publishedAt'],
            'source': article['source']['name'],
            'sentiment_score': sentiment_data['score'],
            'sentiment': sentiment_data['sentiment']
        })
    
    return processed_articles

@app.route('/')
def index():
    """Main route to display the sentiment analysis dashboard."""
    return render_template('index.html')

@app.route('/api/news-sentiment')
def get_news_sentiment():
    """API endpoint to get analyzed news data."""
    articles = fetch_financial_news()
    analyzed_articles = process_news_data(articles)
    
    # Calculate average sentiment
    if analyzed_articles:
        avg_sentiment = sum(a['sentiment_score'] for a in analyzed_articles) / len(analyzed_articles)
    else:
        avg_sentiment = 0
    
    return jsonify({
        'articles': analyzed_articles,
        'average_sentiment': round(avg_sentiment, 2)
    })

if __name__ == '__main__':
    app.run(debug=True, port=8080)