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
    """
    This class handles the fetching of news articles from various sources,
    including location-specific news, default topic-based news, and filtering
    based on language. It interacts with the GNews API to retrieve articles 
    based on user preferences and location.
    """

    def __init__(self, feeds_file: str = "config/news_sources.json"):
        """
        Initializes the NewsFetcher instance. Ensures the config directory exists 
        and creates a default configuration for news sources if it doesn't exist.

        Args:
            feeds_file (str): Path to the news sources configuration file.
        """
        # Ensure the config directory exists
        os.makedirs("config", exist_ok=True)

        # Create default configuration if the news sources file doesn't exist
        if not os.path.exists(feeds_file):
            default_feeds = self._get_default_feeds()
            with open(feeds_file, "w") as f:
                json.dump(default_feeds, f, indent=4)

        # Set the timezone to UTC
        self.timezone = pytz.UTC
        
        # Get the GNews API key from environment variables
        self.gnews_api_key = os.getenv("GNEWS_API_KEY", "")

    def _fetch_gnews_news(self, query: str) -> List[Dict]:
        """
        Fetch news articles from the GNews API based on a search query.

        Args:
            query (str): The search query for news retrieval.

        Returns:
            List[Dict]: A list of dictionaries representing the fetched articles.
        """
        articles = []
        try:
            print(f"===>Query: {query}")
            url = "https://gnews.io/api/v4/search"

            params = {
                "q": query,
                "lang": "en",
                "max": 100,
                "token": self.gnews_api_key,
                "country": "ca",
            }

            response = requests.get(url, params=params)
            if response.status_code != 200:
                print(f"Failed to fetch news: {response.status_code} {response.text}")
                return []

            data = response.json()
            # Parse the returned data and extract article information
            for item in data.get("articles", []):
                title = item.get("title", "")
                link = item.get("url", "")
                snippet = item.get("description", "")
                published_str = item.get("publishedAt", "")

                try:
                    # Convert the published date to a timezone-aware datetime object
                    published = datetime.fromisoformat(published_str.rstrip("Z")).replace(tzinfo=pytz.UTC)
                except Exception:
                    # If parsing fails, set the current UTC time as the published date
                    published = datetime.now(self.timezone)

                try:
                    # Skip non-English articles using the language detection library
                    if detect(title) != "en":
                        continue
                except LangDetectException:
                    # In case language detection fails, skip the article
                    continue
                
                if title and link:
                    articles.append({
                        "title": title,
                        "summary": snippet,
                        "link": link,
                        "published": published,
                        "source": item.get("source", {}).get("name", "GNews"),
                        "category": "general"
                    })

            # If articles are found, return them; otherwise, return an empty list
            if articles:
                return articles
            else:
                print(f"No news results found for '{query}'.")
                return []
            
        except Exception as e:
            print(f"Error fetching news from GNews: {str(e)}")
            return []

    def _get_default_feeds(self) -> Dict:
        """
        Returns a dictionary of default search queries for general news topics.
        These queries are used when no location-specific news is found.

        Returns:
            Dict: A dictionary containing default news topic queries and categories.
        """
        return {
            "default": [
                {"name": "General News", "query": "latest news", "category": "general"},
                {"name": "Technology News", "query": "latest technology news", "category": "technology"},
                {"name": "Business News", "query": "latest business news", "category": "business"},
                {"name": "Sports News", "query": "latest sports news", "category": "sports"},
                {"name": "Health News", "query": "latest health news", "category": "health"},
            ]
        }

    def _get_location_query(self, location: Dict) -> str:
        """
        Generate a location-specific search query to fetch local news.

        Args:
            location (Dict): A dictionary containing city and state information.

        Returns:
            str: A location-based search query string.
        """
        city = location["city"].replace(" ", "+")
        state = location["state"]
        return f"{city} {state} local news"

    def fetch_news(self, location: Dict) -> List[Dict]:
        """
        Fetch news articles using location-specific and default queries.

        Args:
            location (Dict): A dictionary containing city and state information.

        Returns:
            List[Dict]: A list of sorted and unique articles retrieved from the GNews API.
        """
        articles = []

        # Step 1: Use location-specific search query
        try:
            location_query = self._get_location_query(location)
            articles.extend(self._fetch_gnews_news(location_query))
            sleep(uniform(1, 2))  # Adding a delay to avoid hitting rate limits
        except Exception as e:
            print(f"Error fetching location-specific news: {str(e)}")

        # Step 2: Use default search queries if not enough articles
        if len(articles) < 10:
            try:
                default_feeds = self._get_default_feeds()["default"]
                for feed in default_feeds:
                    query = feed["query"]
                    articles.extend(self._fetch_gnews_news(query))
                    sleep(uniform(1, 2))  # Adding a delay between queries
            except Exception as e:
                print(f"Error fetching default news: {str(e)}")

        # Step 3: Sort articles by published date and remove duplicates
        unique_articles = self._remove_duplicates(articles)
        sorted_articles = sorted(unique_articles, key=lambda x: x["published"], reverse=True)

        return sorted_articles

    def _remove_duplicates(self, articles: List[Dict]) -> List[Dict]:
        """
        Removes duplicate articles based on title similarity.

        Args:
            articles (List[Dict]): A list of articles.

        Returns:
            List[Dict]: A list of unique articles.
        """
        seen_titles = set()
        unique_articles = []

        for article in articles:
            title_key = article["title"].lower()
            if title_key not in seen_titles:
                seen_titles.add(title_key)
                unique_articles.append(article)

        return unique_articles
