
from getFeeds import getFeeds
from parse_google_alerts_rss import parse_google_alerts_rss

feeds = getFeeds()

parsedFeeds = []

for feed in feeds:
    parsed = parse_google_alerts_rss(feed[1])
    parsedFeeds.append((
        feed[0],
        parsed,
    ))

for feed in parsedFeeds:
    print("keyword: ", feed[0]) # Google Alert Keyword
    print("\n")
    for link in feed[1]:
        print("title: ", link[0])
        print("url: ", link[1])
        print("summary: ", link[2])
        print("\n")