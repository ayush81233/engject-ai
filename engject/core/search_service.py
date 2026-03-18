import os
import requests
from dotenv import load_dotenv
from duckduckgo_search import DDGS

load_dotenv()

# =========================================
# API KEYS
# =========================================

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")
BRAVE_API_KEY = os.getenv("BRAVE_API_KEY")


# =========================================
# GOOGLE SEARCH
# =========================================

def google_search(query):

    if not GOOGLE_API_KEY or not GOOGLE_CSE_ID:
        return []

    try:

        url = "https://www.googleapis.com/customsearch/v1"

        params = {
            "key": GOOGLE_API_KEY,
            "cx": GOOGLE_CSE_ID,
            "q": query,
            "num": 5
        }

        response = requests.get(url, params=params, timeout=8)

        if response.status_code != 200:
            print("Google API error:", response.text)
            return []

        data = response.json()

        results = []

        for item in data.get("items", []):

            image = None

            if "pagemap" in item:
                images = item["pagemap"].get("cse_image")

                if images:
                    image = images[0].get("src")

            results.append({
                "title": item.get("title"),
                "description": item.get("snippet"),
                "link": item.get("link"),
                "image": image
            })

        return results

    except Exception as e:

        print("Google search failed:", e)

        return []


# =========================================
# BRAVE SEARCH
# =========================================

def brave_search(query):

    if not BRAVE_API_KEY:
        return []

    try:

        url = "https://api.search.brave.com/res/v1/web/search"

        headers = {
            "Accept": "application/json",
            "X-Subscription-Token": BRAVE_API_KEY
        }

        params = {
            "q": query,
            "count": 5
        }

        response = requests.get(url, headers=headers, params=params, timeout=8)

        if response.status_code != 200:
            return []

        data = response.json()

        results = []

        for item in data.get("web", {}).get("results", []):

            results.append({
                "title": item.get("title"),
                "description": item.get("description"),
                "link": item.get("url"),
                "image": None
            })

        return results

    except Exception as e:

        print("Brave search failed:", e)

        return []


# =========================================
# DUCKDUCKGO SEARCH
# =========================================

def duckduckgo_search(query):

    try:

        results = []

        with DDGS() as ddgs:

            search_results = ddgs.text(query, max_results=5)

            for r in search_results:

                results.append({
                    "title": r.get("title"),
                    "description": r.get("body"),
                    "link": r.get("href"),
                    "image": None
                })

        return results

    except Exception as e:

        print("DuckDuckGo search failed:", e)

        return []


# =========================================
# HYBRID SEARCH ENGINE
# =========================================

def hybrid_search(query):

    results = []

    try:
        google_results = google_search(query)
        if google_results:
            results.extend(google_results)
    except:
        pass

    try:
        duck_results = duckduckgo_search(query)
        if duck_results:
            results.extend(duck_results)
    except:
        pass

    # remove duplicates
    seen = set()
    unique_results = []

    for r in results:
        if r["title"] not in seen:
            seen.add(r["title"])
            unique_results.append(r)

    return {
        "results": unique_results[:8]
    }