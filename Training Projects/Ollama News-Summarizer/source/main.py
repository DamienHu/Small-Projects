from news_fetcher import NewsFetcher
from summarizer import NewsSummarizer
from filter_engine import ArticleFilter
import json
import os

def main():
    """
    Main function to execute the local news summarizer process. This function:
    1. Loads user preferences from a JSON configuration file.
    2. Initializes the necessary components for news fetching, filtering, and summarizing.
    3. Fetches news based on the user's location.
    4. Filters the fetched news based on the user's interests.
    5. Generates summaries for the filtered articles and prints them in a readable format.
    """
    
    # Get the directory where this script resides to form the config file path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define the path to the user preferences JSON file
    config_path = os.path.join(script_dir, "config", "user_preferences.json")

    # Open and load the JSON config file containing user preferences
    with open(config_path, 'r', encoding='utf-8') as f:
        preferences = json.load(f)

    # Initialize components: news fetcher, summarizer, and article filter
    fetcher = NewsFetcher()        # Handles fetching news articles
    summarizer = NewsSummarizer()  # Handles generating summaries for articles
    filter_engine = ArticleFilter()  # Filters articles based on interests and time

    # Fetch news articles based on the location from user preferences
    articles = fetcher.fetch_news(preferences["location"])

    # Filter the fetched articles based on the user's selected interests
    filtered_articles = filter_engine.filter_articles(
        articles, preferences["interests"]
    )

    # Generate summaries for each filtered article and print them
    for article in filtered_articles:
        # Generate a summary for the current article
        summary = summarizer.generate_summary(article)
        
        # Print the article's title, source, summary, and link in a readable format
        print(f"\nTitle: {article['title']}")
        print(f"Source: {article['source']}")
        print(f"Summary: {summary}")
        print(f"Link: {article['link']}\n")
        
        # Print a separator line for readability
        print("-" * 80)

# Check if this script is being run directly, and if so, call the main function
if __name__ == "__main__":
    main()
