import asyncio
from typing import Optional
import google.generativeai as genai
import json
import os
import time
from dotenv import load_dotenv
from pydantic import BaseModel, Field
import requests

from get_all_feed_contents import get_all_feed_contents
load_dotenv()

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

INPUT_FILE = "./page_content.json"

MODEL_NAME = "gemini-2.0-flash-lite"

# TODO: refine
EXTRACTION_PROMPT = """
From the document text provided below, extract key details about any military or arms exports. More specifically, look for the following fields:

    transaction_type - Type of transaction (e.g., "Purchase Order", "Subcontract")
    company_division - Company or division name
    recipient - Recipient of the transaction
    amount - Transaction amount (defaults to 0)
    description - Transaction description
    address_1, address_2, city, province, region, postal_code - Address fields
    source_date - Date in YYYY-MM-DD format
    source_description - Source description
    grant_type - Type of grant
    commodity_class - Commodity classification
    contract_number - Contract number
    comments - Additional comments
    is_primary - Boolean flag (defaults to false)


Do not hallucinate. If a field cannot be detemined from the text, leave it empty.

---
DOCUMENT TEXT:
{text_content}
"""

SCHEMA = {
  "type": "object",
  "properties": {
    "transaction_type": {
      "type": "string",
      "description": "Type of transaction (e.g., 'Purchase Order', 'Subcontract')"
    },
    "company_division": {
      "type": "string",
      "description": "Company or division name"
    },
    "recipient": {
      "type": "string",
      "description": "Recipient of the transaction"
    },
    "amount": {
      "type": "number",
      "description": "Transaction amount",
    },
    "description": {
      "type": "string",
      "description": "Transaction description"
    },
    "address_1": {
      "type": "string",
      "description": "Address line 1"
    },
    "address_2": {
      "type": "string",
      "description": "Address line 2"
    },
    "city": {
      "type": "string",
      "description": "City"
    },
    "province": {
      "type": "string",
      "description": "Province/State"
    },
    "region": {
      "type": "string",
      "description": "Region"
    },
    "postal_code": {
      "type": "string",
      "description": "Postal code"
    },
    "source_date": {
      "type": "string",
      "format": "date-time",
      "description": "Date in YYYY-MM-DD format"
    },
    "source_description": {
      "type": "string",
      "description": "Source description"
    },
    "grant_type": {
      "type": "string",
      "description": "Type of grant"
    },
    "commodity_class": {
      "type": "string",
      "description": "Commodity classification"
    },
    "contract_number": {
      "type": "string",
      "description": "Contract number"
    },
    "comments": {
      "type": "string",
      "description": "Additional comments"
    },
    "is_primary": {
      "type": "boolean",
      "description": "Boolean flag indicating if it's primary",
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
            if ("transaction_type" in extracted_info) and  ("company_division" in extracted_info) and ("recipient" in extracted_info):
                print("   ✔️ Found relevant info")
                all_extracted_deals.append(extracted_info)
            else:
                print("   ❌ insufficient info")
        
        # Add a small delay to respect API rate limits (1 second is safe)
        time.sleep(1)

    if all_extracted_deals:
        for transaction in all_extracted_deals:
            requests.post("https://ploughshares.nixc.us/api/transaction", json=transaction)
    else:
        print("\nNo relevant deals were extracted from any of the pages.")

if __name__ == "__main__":
    asyncio.run(main())