import asyncio
import json
from clean_string import clean_string
from fetch_site import fetch_site
from get_feeds import get_feeds
from get_links_from_feed import get_links_from_feed


async def get_all_feed_contents():
    feeds = get_feeds()
    urls = []
    for keyword, feed in feeds:
        alerts = get_links_from_feed(feed)
        for alert in alerts:
            urls.append(alert.url)
    pages = []
    for url in urls:
        content = await fetch_site(url)
        if not content:
            continue
        pages.append({
            "url": url,
            "content": clean_string(content)
        })
    return pages

async def main():
    print(await get_all_feed_contents())

if __name__ == "__main__":
    asyncio.run(main())