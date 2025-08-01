from get_feeds import get_feeds
from get_links_from_feed import get_links_from_feed

feeds = get_feeds()

parsedFeeds = []

for feed in feeds:
    parsed = get_links_from_feed(feed[1])
    parsedFeeds.append((
        feed[0],
        parsed,
    ))

for feed in parsedFeeds:
    print("keyword: ", feed[0]) # Google Alert Keyword
    print("\n")
    for link in feed[1]:
        print("title: ", link.title)
        print("url: ", link.url)
        print("summary: ", link.summary)
        print("\n")