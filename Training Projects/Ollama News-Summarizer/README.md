# Ollama News Summarizer

A Python-based local and global news summarization app that fetches news articles, extracts full content, and generates concise summaries using AI-powered summarization. The app prioritizes local news based on user location queries and gracefully handles incomplete data or paywalled articles.

---

## Features

- Fetches news articles using the **GNews API** (replacing DuckDuckGo search for better article-focused results).
- Extracts full article text using `newspaper3k` with robust error handling and content validation.
- Generates clean, concise summaries with a structured format:  
  - Main Point (1 sentence)  
  - Key Details (1-2 sentences)  
  - Local Impact (1 sentence)
- Prioritizes local news based on user location input.
- Filters and removes duplicate articles.
- User-friendly UI built with **Streamlit** for easy interaction.
- Handles common web scraping and SSL errors.
- Configurable with JSON feed files and environment variables for API keys.

---

## Getting Started

### Prerequisites

- Python 3.7 or later
- GNews API key (you can get a free API key at [https://gnews.io/](https://gnews.io/))
- Recommended to use a virtual environment

### Installation

1. Clone this repository:

``` git clone https://github.com/DamienHu/Small-Projects/tree/main/Training%20Projects/Ollama%20News-Summarizer ```
``` cd ollama-news-summarizer ```

text

2. Create and activate a virtual environment:

``` python -m venv venv ```
source venv/bin/activate # On Windows: venv\Scripts\activate

3. Install the dependencies:

``` pip install -r requirements.txt ```

4. Download NLTK data:

Run Python interpreter and download `punkt` tokenizer:

import nltk
nltk.download('punkt')

5. Download Newspaper3k corpora:

``` python -m newspaper.download_corpora ```

### Configuration

- Set your **GNews API key** as an environment variable:

- On Linux/macOS:
 ```
 export GNEWS_API_KEY="your_api_key_here"
 ```
- On Windows PowerShell:
 ```
 setx GNEWS_API_KEY "your_api_key_here"
 ```
 Then restart your terminal or IDE to make sure the variable is loaded.

- (Optional) Customize `config/news_sources.json` for your default news topic queries or add local feeds.

---

## Usage

Run the app using Streamlit:

``` streamlit run source/app.py ```

text

- The app will open a browser window at `http://localhost:8502`.
- Enter your location to prioritize local news.
- Browse through expandable tabs with summarized articles.
- Click links to read full articles externally.

---

## Project Structure

/
├── config/
│ └── news_sources.json # Default news feed queries
├── source/
│ ├── app.py # Main Streamlit app
│ ├── news_fetcher.py # News fetching (GNews integration)
│ ├── summarizer.py # AI summarization logic
│ ├── filter_engine.py # Article filtering utilities
│ ├── location_service.py # Location services
│ └── requirements.txt # Python dependencies
├── README.md # This file

---

## Dependencies

- `streamlit` - Web UI framework
- `requests` - HTTP requests
- `python-dateutil` - Date parsing
- `nltk` - NLP toolkit for tokenization
- `geocoder` - Geolocation
- `pytz` - Timezone handling
- `langdetect` - Language detection
- `openai` - OpenAI API client (for summarization)
- `newspaper3k` - Article extraction & parsing
- `urllib3` - HTTP retries and connection pooling
- `feedparser` - RSS feed parser (if applicable)

---

## Troubleshooting

- **Missing API key error:**  
  Make sure your `GNEWS_API_KEY` environment variable is set correctly and visible to your Python environment.

- **Extraction errors or no summaries:**  
  Some URLs may point to category pages or be behind paywalls. The app skips very short or invalid article content to maintain summary quality.

- **SSL Errors when fetching articles:**  
  Check your network/proxy settings, and ensure your packages (`requests`, `urllib3`) are up to date.

- **NLTK or Newspaper missing corpora errors:**  
  Download corpora as shown above using `nltk.download('punkt')` and `newspaper.download_corpora`.

---
