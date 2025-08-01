import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

async def fetch_site(url: str) -> str | None:
    """
    Fetches the text content of a URL using Playwright.

    Args:
        url: The URL of the website to fetch.

    Returns:
        A string containing the text content of the page, or None on error.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        try:
            # Change 'networkidle' to 'domcontentloaded' and increase timeout as a fallback
            await page.goto(url, wait_until='domcontentloaded', timeout=60000)
            
            content = await page.content()
            soup = BeautifulSoup(content, 'html.parser')
            
            # .get_text() is the standard method in modern BeautifulSoup
            return soup.get_text()
            
        except Exception as e:
            print(f"An error occurred: {e}")
            return None
            
        finally:
            await browser.close()