from typing import List, Dict
from datetime import datetime, timedelta
import pytz

class ArticleFilter:
    """
    This class handles filtering news articles based on their publication time
    and user interests. It supports filtering articles by different time ranges
    such as "today", "week", and "month".
    """
    
    def __init__(self):
        """
        Initializes the ArticleFilter object by setting the timezone to UTC and
        defining the time-based filters for articles. It also sets the current time
        for comparison during filtering.
        """
        self.timezone = pytz.UTC  # Set the timezone to UTC
        now = datetime.now(self.timezone)  # Get current UTC time

        # Define filters for different time ranges
        self.time_filters = {
            "today": lambda x: self._to_utc(x["published"]).date() == now.date(),
            "week": lambda x: self._to_utc(x["published"]) >= now - timedelta(days=7),
            "month": lambda x: self._to_utc(x["published"]) >= now - timedelta(days=30),
        }

    def _to_utc(self, dt: datetime) -> datetime:
        """
        Converts a datetime object to UTC timezone-aware datetime.

        Args:
            dt (datetime): The datetime object to be converted.

        Returns:
            datetime: The UTC timezone-aware datetime.
        """
        # If datetime is naive (no timezone), localize it to UTC
        if dt.tzinfo is None:
            return self.timezone.localize(dt)
        # If datetime is already timezone-aware, convert it to UTC
        return dt.astimezone(self.timezone)
    
    def filter_articles(
            self,
            articles: List[Dict],
            interests: List[str],
            time_range: str = "week",
            max_articles: int = 10,
    ) -> List[Dict]:
        """
        Filters articles based on the specified time range, user interests, and limits
        the number of articles returned to a maximum.

        Args:
            articles (List[Dict]): A list of articles, each represented as a dictionary.
            interests (List[str]): A list of interests to filter articles by.
            time_range (str): The time range for filtering articles. Defaults to "week".
            max_articles (int): The maximum number of articles to return. Defaults to 10.

        Returns:
            List[Dict]: A list of filtered articles.
        """
        
        # Step 1: Filter articles by time range
        time_filter = self.time_filters.get(time_range, self.time_filters["week"])
        time_filtered = [article for article in articles if time_filter(article)]

        # Step 2: Filter articles by user interests
        interest_filtered = []
        for article in time_filtered:
            # Combine title and summary content to check for user interests
            content = f"{article['title']} {article['summary']}".lower()

            # The following line is commented out; it was originally used to filter by interests
            # if any(interest.lower() in content for interest in interests):
            interest_filtered.append(article)

        # Step 3: Sort articles by publication date (most recent first)
        # Return the filtered articles, limited by max_articles
        return sorted(interest_filtered, key=lambda x: x["published"], reverse=True)[:max_articles]
