import json
from typing import List, Dict
from datetime import datetime
from dateutil import parser
import requests
import re
import os
from time import sleep
from random import uniform
import pytz
from langdetect import detect, LangDetectException

class NewsFetcher:
    def __init__(self, feeds_file: str = "config/news_sources.json"):
        #Ensure config directory exists
        os.makedirs("config", exist_ok=True)

        #Create default config if it doesn't exist
        if not os.path.exists(feeds_file):
            default_feeds = self._get_default_feeds()
            with open(feeds_file, "w") as f:
                json.dump(default_feeds,f, indent=4)

        self.timezone = pytz.UTC
        self.gnews_api_key = os.getenv("GNEWS_API_KEY", "")

    def _fetch_gnews_news(self, query: str)-> List[Dict]:
        """Fetch news using DuckDuckGo search"""
        articles = []
        try:
            print(f"===>Query: {query}")
            url = "https://gnews.io/api/v4/search"

            params = {
                "q": query,
                "lang": "en",
                "max": 100,
                "token":self.gnews_api_key,
                "country":"ca",
            }

            response = requests.get(url, params=params)
            if response.status_code !=200:
                print(f"Failed to fetch news: {response.status_code} {response.text}")
                return[]

            data = response.json()
            for item in data.get("articles",[]):
                title = item.get("title","")
                link = item.get("url","")
                snippet = item.get("description","")
                published_str = item.get("plublishedAt","")

                try:
                    published = datetime.fromisoformat(published_str.rstrip("Z")).replace(tzinfo=pytz.UTC)
                except Exception:
                    published = datetime.now(self.timezone)

                try:
                    if detect(title) != "en":
                        continue
                except LangDetectException:
                    continue
                
                if title and link:
                    articles.append({
                        "title":title,
                        "summary":snippet,
                        "link":link,
                        "published": published,
                        "source": item.get("source",{}).get("name","GNews"),
                        "category": "general"
                    })
                
            if articles:
                return articles
            else:
                print(f"No news results found for '{query}'.")
                return []
            
        except Exception as e:
            print(f"Error fetching news from GNews: {str(e)}")
            return []

        
    def _get_default_feeds(self)->Dict:
        """Get default search queries for general news topics"""
        return {
            "default": [
                {"name": "General News", "query": "latest news", "category": "general"},
                {
                    "name": "Technology News",
                    "query": "latest technology news",
                    "category": "technology",
                },
                {
                    "name": "Business News",
                    "query": "latest business news",
                    "category": "business",
                },
                {
                    "name": "Sports News",
                    "query": "latest sports news",
                    "category": "sports",
                },
                {
                    "name": "Health News",
                    "query": "latest health news",
                    "category": "health",
                },
            ]
        }
    
    def _get_location_query(self, location: Dict) -> str:
        """Generate a search query based on location"""
        city = location["city"].replace(" ","+")
        state = location["state"]
        return f"{city} {state} local news"
    
    def fetch_news(self, location: Dict) -> List[Dict]:
        """Fetch news using DuckDuckGo search queries"""
        articles = []

        #1. Use location-specific search query
        try:
            location_query = self._get_location_query(location)
            articles.extend(self._fetch_gnews_news(location_query))
            sleep(uniform(1,2)) #Adding a delay to avoid hitting rate limits
        except Exception as e:
            print(f"Error fetching location-specific news: {str(e)}")

        #2. Use default search queries if not enough articles
        if len(articles) < 10:
            try:
                default_feeds = self._get_default_feeds()["default"]
                for feed in default_feeds:
                    query = feed["query"]
                    articles.extend(self._fetch_gnews_news(query))
                    sleep(uniform(1,2)) #Adding a delay between queries
            except Exception as e:
                print(f"Error fetching default news: {str(e)}")

        #3. Sort by date and remove duplicates
        unique_articles = self._remove_duplicates(articles)
        sorted_articles = sorted(unique_articles, key = lambda x: x["published"], reverse= True)

        return sorted_articles
    
    def _remove_duplicates(self, articles: List[Dict]) -> List[Dict]:
        """Remove duplicate articles based on title similarity"""
        seen_titles = set()
        unique_articles = []

        for article in articles:
            title_key = article["title"].lower()
            if title_key not in seen_titles:
                seen_titles.add(title_key)
                unique_articles.append(article)

        return unique_articles