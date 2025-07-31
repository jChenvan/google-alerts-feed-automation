from bs4 import BeautifulSoup
import feedparser
import urllib.parse

def parse_google_alerts_rss(rss_url: str) -> list[tuple[str, str]]:
    """
    Parses a Google Alerts RSS feed URL and extracts the title and clean URL for each alert.

    Args:
        rss_url: The URL of the Google Alerts RSS feed.

    Returns:
        A list of tuples, where each tuple contains the title and the direct URL
        of an alert. Returns an empty list if the feed cannot be parsed or is empty.
    """
    alerts = []
    # Parse the RSS feed from the provided URL
    feed = feedparser.parse(rss_url)

    # Check if the feed was parsed successfully and has entries
    if feed.bozo:
        print(f"Error parsing feed: {feed.bozo_exception}")
        return alerts

    # Iterate over each entry in the feed
    for entry in feed.entries:
        # The title is directly available
        title_raw = entry.title
        title_soup = BeautifulSoup(title_raw, "html.parser") # type: ignore
        title = title_soup.get_text()

        # The summary often contains HTML, so we'll parse it to get clean text.
        # This removes any HTML tags like <b> for a cleaner summary.
        summary_html = entry.summary
        soup = BeautifulSoup(summary_html, 'html.parser') # type: ignore
        summary = soup.get_text()

        # The link is a Google redirect URL. We need to extract the 'url' parameter.
        # Example link: https://www.google.com/url?rct=j&sa=t&url=https://www.example.com/story&ct=ga&cd=CA...
        link = entry.link

        try:
            # Parse the URL to easily access its components
            parsed_url = urllib.parse.urlparse(link) # type: ignore
            # Get the query parameters as a dictionary
            query_params = urllib.parse.parse_qs(parsed_url.query)
            # The actual destination URL is in the 'url' parameter
            actual_url = query_params.get('url', [None])[0]

            if actual_url:
                # Add the title and the clean URL to our list
                alerts.append((title, actual_url, summary))
        except Exception as e:
            print(f"Could not parse URL for entry '{title}': {e}")


    return alerts

