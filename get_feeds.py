import json
import os

def get_feeds() -> list[tuple[str, str]]:
    """Reads feed names and URLs from a local JSON file.

    This function opens 'feeds.json', which is expected to be in the
    same directory as this script. It parses the JSON object, which
    should contain string keys (feed names) and string values (URLs).

    Returns:
        list[tuple[str, str]]: A list of tuples, where each tuple
                               contains a feed's name and its URL.
    """
    file_path = os.path.join(os.path.dirname(__file__), "./feeds.json")
    with open(file_path, "r") as f:
        data: dict[str, str] = json.load(f)
    return list(data.items())