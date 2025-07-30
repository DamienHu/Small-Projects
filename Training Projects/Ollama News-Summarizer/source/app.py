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

API_KEY = "pk.33a3197be1753cc405b82e783d923fb4"

def load_configs():
    config_file = "config/user_preferences.json"
    os.makedirs("config",exist_ok=True)

    if not os.path.exists(config_file):
        default_config = {"interests": ["politics","technology","sports","weather"]}
        with open(config_file, "w") as f:
            json.dump(default_config, f, indent = 4)

    with open(config_file, 'r') as f:
        return json.load(f)
    
def save_preferences(interests: List[str]):
    os.makedirs("config", exist_ok=True)
    preferences = {"interests": interests}
    with open("config/user_preferences.json","w") as f:
        json.dump(preferences,f,indent=4)

def fetch_autocomplete(query):
    url = f"https://us1.locationiq.com/v1/autocomplete.php?key={API_KEY}&q={query}&format=json&limit=5"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return []

def main():
    st.set_page_config(page_title="Local News Summarizer", layout="wide")
    st.title("🗞️ AI-Powered Local News Summarizer")

    #Initialize components
    location_service = LocationService()
    fetcher = NewsFetcher()
    summarizer = NewsSummarizer()
    filter_engine = ArticleFilter()

    #Load current preferences
    preferences = load_configs()

    #Sidebar for preferences
    with st.sidebar:
        st.header("📋 Preferences")

        #Display detected location
        st.subheader("📍 Enter your address")
        
        typed = st.text_input("Start typing your address:")

        suggestions = []
        user_location_override = None
        if typed:
            suggestions = fetch_autocomplete(typed)

        if suggestions:
            options = [item.get("display_name") for item in suggestions]
            selected = st.selectbox("Select your address",options)

            if selected:
                selected_item = next((item for item in suggestions if item["display_name"]== selected), None)

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
                    
        location = location_service.get_location(user_override=user_location_override)
        
        
        #Interest selector
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
        interests = st.multiselect(
            "Select your interest",
            available_interest,
            default=preferences["interests"],
        )

        #Time range selector
        time_range = st.radio("Time range",["today", "week", "month"], index =1)

        if st.button("Save Preferences"):
            save_preferences(interests)
            st.success("Preferences saved!")
    
    #Main content
    if not interests:
        st.warning("Please select at least one interest in the sidebar.")
        return
    
    with st.spinner("Fetching local news..."):
        articles = fetcher.fetch_news(location)
        filtered_articles = filter_engine.filter_articles(
            articles, interests, time_range
        )

    if not filtered_articles:
        st.info(
            "No articles found matching your interests. Try adjusting your filters."
        )
        return
    
    #Display articles
    for article in filtered_articles:
        with st.expander(f"📰 {article['title']}", expanded=False):
            col1, col2 = st.columns([2,1])

            with col1:
                st.markdown(f"**Source:** {article}")
                st.markdown(f"**Published:** {article['published'].strftime('%Y-%m-%d %H:%M')}")

                with st.spinner("Generating summary..."):
                    summary = summarizer.generate_summary(article)
                st.markdown("### Summary")
                st.write(summary)
            with col2:
                st.markdown("### Original Article")
                st.link_button('Read Full Article', article["link"])

if __name__ == "__main__":
    main()