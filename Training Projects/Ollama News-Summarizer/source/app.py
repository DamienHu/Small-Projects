import streamlit as st
import json
from news_fetcher import NewsFetcher
from summarizer import NewsSummarizer
from filter_engine import ArticleFilter
from location_service import LocationService
from datetime import datetime
from typing import List
import os
import requests


# API key for LocationIQ API service
API_KEY = "pk.33a3197be1753cc405b82e783d923fb4"

def load_configs():
    """
    Load user preferences from a JSON configuration file. If the file does not exist,
    create it with default values for user interests.

    Returns:
        dict: A dictionary containing the user preferences (interests).
    """
    config_file = "config/user_preferences.json"
    
    # Ensure the config directory exists
    os.makedirs("config", exist_ok=True)

    # Create a default configuration if the file doesn't exist
    if not os.path.exists(config_file):
        default_config = {"interests": ["politics", "technology", "sports", "weather"]}
        with open(config_file, "w") as f:
            json.dump(default_config, f, indent=4)

    # Read and return the configuration from the file
    with open(config_file, 'r') as f:
        return json.load(f)
    
def save_preferences(interests: List[str]):
    """
    Save the user preferences to a JSON configuration file.

    Args:
        interests (List[str]): A list of interests selected by the user.
    """
    os.makedirs("config", exist_ok=True)
    preferences = {"interests": interests}
    
    # Write preferences to the JSON file
    with open("config/user_preferences.json", "w") as f:
        json.dump(preferences, f, indent=4)

def fetch_autocomplete(query):
    """
    Fetch autocomplete suggestions for a given address query from the LocationIQ API.

    Args:
        query (str): The address query to be autocompleted.

    Returns:
        list: A list of autocomplete suggestions, or an empty list if the request fails.
    """
    url = f"https://us1.locationiq.com/v1/autocomplete.php?key={API_KEY}&q={query}&format=json&limit=5"
    
    # Send request to the LocationIQ API
    response = requests.get(url)
    
    # Return JSON response if successful, otherwise return an empty list
    if response.status_code == 200:
        return response.json()
    return []

def main():
    """
    The main function that sets up the Streamlit app, loads user preferences,
    handles user input, and displays local news articles with summaries.
    """
    st.set_page_config(page_title="Local News Summarizer", layout="wide")
    st.title("🗞️ AI-Powered Local News Summarizer")

    # Initialize necessary components
    location_service = LocationService()
    fetcher = NewsFetcher()
    summarizer = NewsSummarizer()
    filter_engine = ArticleFilter()

    # Load the current user preferences (interests)
    preferences = load_configs()

    # Sidebar for user preferences and inputs
    with st.sidebar:
        st.header("📋 Preferences")

        # Display address input and autocomplete suggestions
        st.subheader("📍 Enter your address")
        typed = st.text_input("Start typing your address:")

        suggestions = []
        user_location_override = None
        
        # Fetch autocomplete suggestions if the user is typing
        if typed:
            suggestions = fetch_autocomplete(typed)

        # If suggestions are available, present them in a selectbox
        if suggestions:
            options = [item.get("display_name") for item in suggestions]
            selected = st.selectbox("Select your address", options)

            # If a location is selected, extract details from the autocomplete result
            if selected:
                selected_item = next((item for item in suggestions if item["display_name"] == selected), None)
                if selected_item:
                    address = selected_item.get("address", {})
                    user_location_override = {
                        "city": address.get("city") or address.get("town") or address.get("village") or "",
                        "state": address.get("state") or address.get("province") or "",
                        "country": address.get("country") or "",
                    }
                    st.write(f"City: {user_location_override['city']}")
                    st.write(f"State: {user_location_override['state']}")
                    st.write(f"Country: {user_location_override['country']}")

        # Retrieve location details from the LocationService based on user input
        location = location_service.get_location(address=user_location_override)
        
        # Interest selector for the user
        available_interest = [
            "politics",
            "technology",
            "sports",
            "weather",
            "education",
            "health",
            "business",
            "entertainment",
        ]
        
        # Let the user select their interests
        interests = st.multiselect(
            "Select your interest",
            available_interest,
            default=preferences["interests"],
        )

        # Time range selector for news articles
        time_range = st.radio("Time range", ["today", "week", "month"], index=1)

        # Save the selected preferences
        if st.button("Save Preferences"):
            save_preferences(interests)
            st.success("Preferences saved!")
    
    # Ensure that at least one interest is selected
    if not interests:
        st.warning("Please select at least one interest in the sidebar.")
        return
    
    # Fetch and filter local news articles based on the user's location and preferences
    with st.spinner("Fetching local news..."):
        articles = fetcher.fetch_news(location)
        filtered_articles = filter_engine.filter_articles(
            articles, interests, time_range
        )

    # Display a message if no articles were found
    if not filtered_articles:
        st.info(
            "No articles found matching your interests. Try adjusting your filters."
        )
        return
    
    # Display the filtered articles with summaries
    for article in filtered_articles:
        print(f"Extracting full text from URL: {article['link']}")
        
        # Extract the full text of the article
        article["full_text"] = summarizer.extract_full_text(article["link"])
        
        with st.expander(f"📰 {article['title']}", expanded=False):
            col1, col2 = st.columns([2, 1])

            with col1:
                st.markdown(f"**Title:** {article['title']}")
                st.markdown(f"**Source:** {article.get('source', 'Unknown')}")
                st.markdown(f"**Published:** {article['published'].strftime('%Y-%m-%d %H:%M')}")
                
                # Generate and display the article summary
                with st.spinner("Generating summary..."):
                    summary = summarizer.generate_summary(article)
                st.markdown("### Summary")
                st.write(summary)
            with col2:
                st.markdown("### Original Article")
                st.link_button('Read Full Article', article["link"])

if __name__ == "__main__":
    # Run the main function if the script is executed directly
    main()
