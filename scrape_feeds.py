import asyncio
from typing import Type
from fetch_site import fetch_site
from get_feeds import get_feeds
from get_links_from_feed import Alert, get_links_from_feed
from get_object_from_string import PydanticModel, get_object_from_string
from schema import Transaction

async def scrape_links(
        links: list[Alert],
        schema: Type[PydanticModel],
        extra_prompts: str | None = None,
) -> list[tuple[str, Type[PydanticModel]]]:
    """Asynchronously scrapes web pages and extracts structured data.

    For each link provided, this function fetches the web content, then uses an LLM
    to parse and extract data according to the provided Pydantic schema.

    Args:
        links: A list of tuples, where each tuple contains a title, URL,
               and summary for a web page.
        schema: The Pydantic model to which the extracted data should conform.
        extra_prompts: Optional additional instructions for the LLM to refine
                       the data extraction process.

    Returns:
        A list of tuples, each containing the source URL and the successfully
        parsed Pydantic object. Links that fail to fetch or parse are omitted.
    """
    res = []
    for l in links:
        url = l.url
        content = await fetch_site(url)
        if not content:
            print("fetch from " + url + " failed.")
            continue
        parsed_content = get_object_from_string(content, schema, extra_prompts)
        if not parsed_content:
            print("parsing content from " + url + " failed.")
            continue
        res.append((url, parsed_content))
    return res


async def scrape_feeds(
        schema: Type[PydanticModel],
        extra_prompts: str | None = None,
) -> list[tuple[str, list[tuple[str, Type[PydanticModel]]]]]:
    """Scrapes articles from RSS feeds and extracts structured data.

    This function retrieves a list of RSS feeds, collects all article links
    from them, and then uses `scrape_links` to process the articles from
    each feed.

    Args:
        schema: The Pydantic model to which the extracted data should conform.
        extra_prompts: Optional additional instructions for the LLM to refine
                       the data extraction process, passed to `scrape_links`.

    Returns:
        A list of tuples, where each tuple contains the feed's name and a list
        of scraping results (URL, Pydantic object) for that feed.
    """
    feeds = get_feeds()
    grouped_links = list(map(lambda f: (
        f[0],
        get_links_from_feed(f[1])
    ), feeds))

    res = []
    for group in grouped_links:
        res.append((group[0], await scrape_links(group[1], schema, extra_prompts)))

    return res

async def main():
    list = await scrape_feeds(Transaction, '''
You have been given the site content for some article.
If the article describes some sort of military weapons transaction involving the Canadian government, extract the relevant details based on the schema.
If the article has nothing to do with a military weapons transaction, leave the fields blank.
Additionally, if there isn't enough information to definitively determine the value of a field, leave it blank.
''')
    for item in list:
        print("keyword:", item[0])
        print("\n")
        for item2 in item[1]:
            print("url:", item2[0])
            print(item2[1])
            print("\n")

if __name__ == "__main__":
    asyncio.run(main())