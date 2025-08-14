from news_fetcher import NewsFetcher
from summarizer import NewsSummarizer
from filter_engine import ArticleFilter
import json
import os


def main():
    # Get the directory where this script resides
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, "config", "user_preferences.json")

    # Open and load the JSON config correctly
    with open(config_path, 'r', encoding='utf-8') as f:
        preferences = json.load(f)

    #Initialize components
    fetcher = NewsFetcher()
    summarizer = NewsSummarizer()
    filter_engine = ArticleFilter()

    #Fetch news for user's location
    articles = fetcher.fetch_news(preferences["location"])

    #Filter based on interests
    filtered_articles = filter_engine.filter_articles(
        articles,preferences["interests"]
    )

    #Genereate summaries
    for article in filtered_articles:
        summary = summarizer.generate_summary(article)
        print(f"\nTitle: {article['title']}")
        print(f"Source: {article['source']}")
        print(f"Summary: {summary}")
        print(f"Link: {article['link']}\n")
        print("-" * 80)

if __name__ == "__main__":
    main()