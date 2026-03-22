import requests
import time
import os

# Get a free key at https://newsapi.org/ (Takes 30 seconds)
API_KEY = "YOUR_NEWS_API_KEY" 
QUERY = "oil prices OR Hormuz OR sovereign debt"

def fetch_live_news():
    url = f"https://newsapi.org/v2/everything?q={QUERY}&sortBy=publishedAt&apiKey={API_KEY}"
    
    try:
        response = requests.get(url)
        articles = response.json().get('articles', [])[:5]
        
        with open("news_feed.txt", "w", encoding="utf-8") as f:
            for art in articles:
                # Format: [CATEGORY] Time - Headline
                source = art['source']['name'].upper()
                title = art['title']
                f.write(f"[{source}] - {title}\n")
        
        print(f"-> news_feed.txt updated at {time.strftime('%H:%M:%S')}")
    except Exception as e:
        print(f"Error fetching news: {e}")

if __name__ == "__main__":
    while True:
        fetch_live_news()
        time.sleep(600) # Wait 10 minutes
