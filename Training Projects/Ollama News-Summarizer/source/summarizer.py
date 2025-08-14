import nltk
import requests
from nltk.tokenize import sent_tokenize
from typing import Dict
from openai import OpenAI
from newspaper import Article
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class NewsSummarizer:
    """
    This class handles the extraction of article text and generation of summaries.
    It uses the OpenAI API for summarization, retrieves the full text from URLs,
    and ensures text extraction is robust by handling retries and SSL issues.
    """

    def __init__(self, base_url: str = "http://localhost:11434/v1"):
        """
        Initializes the NewsSummarizer class, setting up the OpenAI client
        and ensuring that necessary NLTK resources for tokenization are available.

        Args:
            base_url (str): Base URL for the OpenAI service.
        """
        # Initialize the OpenAI client (though it seems to be unused in this context)
        self.client = OpenAI(base_url=base_url, api_key="ollama")

        # Ensure that the NLTK tokenizer resource is available
        try:
            nltk.data.find("tokenizers/punkt")
        except LookupError:
            nltk.download("punkt")

    def _create_messages(self, article: Dict) -> list:
        """
        Create the message payload to send to OpenAI for summarizing the article.
        The summary is created based on the first few sentences of the article's content.

        Args:
            article (Dict): A dictionary representing the article to summarize.

        Returns:
            list: The message structure to send to the OpenAI API.
        """
        # Extract the first few sentences from the article content for context
        content = article["summary"]
        sentences = sent_tokenize(content)
        context = " ".join(sentences[:3])

        # Return the message format that OpenAI will process
        return [
            {
                "role": "system",
                "content": """You are an expert news editor skilled at creating concise, informative summaries of local news articles. Focus on key facts and local impact while maintaining objectivity.""",
            },
            {
                "role": "user",
                "content": f"""Summarize this local news article:
                
                Title: {article['title']}
                Category: {article.get('category', 'general')}
                Content: {context}
                    
                Format your response as:
                1. Main point (1 sentence)
                2. Key details (1-2 sentences)
                3. Local impact (1 sentence)""",
            },
        ]

    def extract_full_text(self, url: str, min_length: int = 200) -> str:
        """
        Extract the full text of an article from the given URL using the Newspaper3k library.
        This method handles retries, SSL errors, and ensures the text is long enough to be useful.

        Args:
            url (str): The URL of the article to fetch and parse.
            min_length (int): Minimum length of the extracted text to be considered valid.

        Returns:
            str: The extracted article text, or an empty string if there were issues.
        """
        headers = {'User-Agent': 'Mozilla/5.0'}
        session = requests.Session()

        # Set up retries in case of failed connections
        retries = Retry(total=3, backoff_factor=0.3, status_forcelist=[500, 502, 503, 504])
        adapter = HTTPAdapter(max_retries=retries)
        session.mount("https://", adapter)

        try:
            # Attempt to retrieve the article page
            response = session.get(url, headers=headers, timeout=10)
            response.raise_for_status()  # Will raise an error if the status code isn't 200
        except requests.exceptions.SSLError as ssl_err:
            print(f"SSL error for {url}: {ssl_err} - trying without verification")
            # Retry the request without SSL verification (risky, use cautiously)
            response = session.get(url, headers=headers, timeout=10, verify=False)
        except Exception as e:
            print(f"Failed to download page {url}: {e}")
            return ""  # Return an empty string if the request fails

        try:
            # Use Newspaper3k to parse the article's content
            article = Article(url)
            article.set_html(response.text)
            article.parse()
            text = article.text.strip()

            # Ensure the extracted text is long enough
            if len(text) < min_length:
                print(f"Extracted text from {url} too short ({len(text)})")
                return ""  # Return empty string if text is too short

            return text  # Return the parsed article text
        except Exception as e:
            print(f"Failed to parse article from {url}: {e}")
            return ""  # Return empty string if parsing fails

    def generate_summary(self, article: Dict) -> str:
        """
        Generate a summary of the article by interacting with the OpenAI API.

        Args:
            article (Dict): A dictionary representing the article to summarize.

        Returns:
            str: The generated summary, or an error message if there was an issue.
        """
        try:
            # Call OpenAI's API to generate a summary based on the messages
            response = self.client.chat.completions.create(
                model="llama3.2",
                messages=self._create_messages(article),
                temperature=0.7,  # Adjust the creativity of the response
                max_tokens=200,  # Limit the number of tokens in the response
            )
            return response.choices[0].message.content  # Return the generated summary

        except Exception as e:
            # Handle any errors that may occur during the OpenAI API call
            return f"Error generating summary: {str(e)}"
