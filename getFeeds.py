import json
import os

def getFeeds():
    with open(os.path.join(os.path.dirname(__file__), "./feeds.json"), "r") as f:
        raw = f.read()

    parsed = json.loads(raw)
    result = list(parsed.items())
    return result 
