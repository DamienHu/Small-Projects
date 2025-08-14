import nltk
import requests
from nltk.tokenize import sent_tokenize
from typing import Dict
from openai import OpenAI
from newspaper import Article
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class NewsSummarizer:
    def __init__(self,base_url: str = "http://localhost:11434/v1"):
        self.client = OpenAI(base_url=base_url, api_key = "ollama") #required but unused
        try:
            nltk.data.find("tokenizers/punkt")
        except LookupError:
            nltk.download("punkt")

    def _create_messages(self, article: Dict)-> list:
        #Extract first few sentances for context
        content = article["summary"]
        sentences = sent_tokenize(content)
        context = " ".join(sentences[:3])

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
    def extract_full_text(self,url: str,min_length = 200) ->str:
        headers = {'User-Agent': 'Mozilla/5.0'}
        session = requests.Session()
        retries = Retry(total=3, backoff_factor=0.3, status_forcelist=[500, 502, 503, 504])
        adapter = HTTPAdapter(max_retries=retries)
        session.mount("https://", adapter)

        try:
            response = session.get(url, headers=headers, timeout=10)
            response.raise_for_status()
        except requests.exceptions.SSLError as ssl_err:
            print(f"SSL error for {url}: {ssl_err} - trying without verification")
            # Retry without verification (riskier, use cautiously)
            response = session.get(url, headers=headers, timeout=10, verify=False)
        except Exception as e:
            print(f"Failed to download page {url}: {e}")
            return ""

        try:
            article = Article(url)
            article.set_html(response.text)
            article.parse()
            text = article.text.strip()
            if len(text) < 200:
                print(f"Extracted text from {url} too short ({len(text)})")
                return ""
            return text
        except Exception as e:
            print(f"Failed to parse article from {url}: {e}")
            return ""
        
    def generate_summary(self, article: Dict)-> str:
        try:
            response = self.client.chat.completions.create(
                model="llama3.2",
                messages=self._create_messages(article),
                temperature=0.7,
                max_tokens=200,
            )
            return response.choices[0].message.content
        
        except Exception as e:
            return f"Error generating summary: {str(e)}"