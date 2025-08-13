import asyncio
import google.generativeai as genai
import json
import os
import time
from dotenv import load_dotenv

from get_all_feed_contents import get_all_feed_contents
load_dotenv()

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

INPUT_FILE = "./page_content.json"

MODEL_NAME = "gemini-2.0-flash-lite"

# TODO: refine
EXTRACTION_PROMPT = """
You are given a news article regarding video games. From the document text provided below, Look for the following fields:

game - name of the video game being discussed
date - date of the news
game_description - a one sentence description of the game
news_description - describe the news as concisely as possible. Use telegraphic style.

Make sure to put the correct information in the correct field.
Do not hallucinate. If a field cannot be detemined from the text or isn't relevant, leave it empty.

---
DOCUMENT TEXT:
{text_content}
"""

SCHEMA = {
  "type": "object",
  "properties": {
    "game": {
      "type": "string",
      "description": "Name of the video game"
    },
    "game_description": {
      "type": "string",
      "description": "a one sentence description of the game"
    },
    "date": {
      "type": "string",
      "format": "date-time",
      "description": "Date of the news"
    },
    "news_description": {
      "type": "string",
      "description": "Concise, telegraphic description of the news"
    }
  }
}


def process_content_with_gemini(text_content):
    """
    Sends the text to the Gemini API with the extraction prompt and
    parses the JSON response.
    """
    model = genai.GenerativeModel(MODEL_NAME) # type: ignore
    prompt = EXTRACTION_PROMPT.format(text_content=text_content)

    try:
        response = model.generate_content(
            prompt,
            generation_config={
                "response_schema": SCHEMA,
                "response_mime_type": 'application/json',
            }
            )
        return json.loads(response.text)
    except Exception as e:
        print(f"   ❌ An error occurred while calling Gemini or parsing its response: {e}")
        return {"error": str(e)}


async def main():
    """Main function to run the data extraction process."""
    if not GOOGLE_API_KEY:
        print("❌ Error: GOOGLE_API_KEY environment variable not set.")
        return

    genai.configure(api_key=GOOGLE_API_KEY) # type: ignore

    print("Retrieving all feed contents...")
    scraped_pages = await get_all_feed_contents()
    if not scraped_pages:
        print("❌ Error: No scraper results found.")
        return
    print("✅ Successfully retrieved all feed contents.")

    all_extracted_deals = []
    total_pages = len(scraped_pages)

    print(f"🤖 Starting information extraction with Gemini for {total_pages} pages...")

    for i, page in enumerate(scraped_pages):
        print(f"\nProcessing page {i+1}/{total_pages}: {page['url']}")

        # Avoid processing pages with very little text
        if len(page.get('content', '')) < 150:
            print("   ⏩ Skipping page due to insufficient content.")
            continue

        extracted_info = process_content_with_gemini(page['content'])
        
        # Check if the extraction was successful and contains actual data
        if extracted_info and "error" not in extracted_info:
            print("   ✔️ Found relevant info")
            all_extracted_deals.append(extracted_info)
            print(f"   Extracted info: {extracted_info}")
        
        # Add a small delay to respect API rate limits (1 second is safe)
        time.sleep(1)

    if all_extracted_deals:
        with open("./result.json", "w", encoding="utf-8") as f:
            json.dump(all_extracted_deals, f, ensure_ascii=False, indent=2)
        print(f"\n✅ Extracted info written to ./result.json")
    else:
        print("\nNo relevant deals were extracted from any of the pages.")

if __name__ == "__main__":
    asyncio.run(main())