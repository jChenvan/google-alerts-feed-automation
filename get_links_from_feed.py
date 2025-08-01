from dataclasses import dataclass
from bs4 import BeautifulSoup
import feedparser
import urllib.parse

@dataclass
class Alert:
    """A simple data class to hold information about a single alert."""
    title: str
    url: str
    summary: str

def get_links_from_feed(rss_url: str) -> list[Alert]:
    """
    Parses a Google Alerts RSS feed URL and extracts the data for each alert.

    Args:
        rss_url: The URL of the Google Alerts RSS feed.

    Returns:
        A list of Alert objects. Returns an empty list if the feed 
        cannot be parsed or is empty.
    """
    alerts: list[Alert] = []
    # Parse the RSS feed from the provided URL
    feed = feedparser.parse(rss_url)

    # Check if the feed was parsed successfully and has entries
    if feed.bozo:
        print(f"Error parsing feed: {feed.bozo_exception}")
        return alerts

    # Iterate over each entry in the feed
    for entry in feed.entries:
        # The title is directly available
        title_soup = BeautifulSoup(entry.title, "html.parser") #type: ignore
        title = title_soup.get_text()

        # The summary often contains HTML, so we parse it to get clean text.
        summary_soup = BeautifulSoup(entry.summary, 'html.parser') #type: ignore
        summary = summary_soup.get_text()

        # The link is a Google redirect URL; we extract the 'url' parameter.
        link = entry.link

        try:
            # Parse the URL to easily access its components
            parsed_url = urllib.parse.urlparse(link) #type: ignore
            # Get the query parameters as a dictionary
            query_params = urllib.parse.parse_qs(parsed_url.query)
            # The actual destination URL is in the 'url' parameter
            actual_url = query_params.get('url', [None])[0]

            if actual_url:
                # Append an Alert object instead of a tuple
                alert_obj = Alert(title=title, url=actual_url, summary=summary)
                alerts.append(alert_obj)
        except Exception as e:
            print(f"Could not parse URL for entry '{title}': {e}")

    return alerts