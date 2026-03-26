import os
import requests
from dotenv import load_dotenv
from duckduckgo_search import DDGS
from concurrent.futures import ThreadPoolExecutor

load_dotenv()

# =========================================
# API KEYS
# =========================================

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")

COMMON_HEADERS = {
    "User-Agent": "EngJect-It-App"
}


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
                "image": image,
                "source": "Google"
            })

        return results

    except Exception as e:
        print("Google search failed:", e)
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
                    "image": None,
                    "source": "DuckDuckGo"
                })

        return results

    except Exception as e:
        print("DuckDuckGo search failed:", e)
        return []


# =========================================
# PROJECT-FOCUSED QUERY BUILDER 🔥
# =========================================

def build_project_query(query):
    return f"{query} engineering project OR final year project OR github OR implementation"


# =========================================
# REMOVE DUPLICATES (IMPROVED)
# =========================================

def deduplicate(results):
    seen_links = set()
    unique_results = []

    for r in results:
        link = r.get("link")

        if link and link not in seen_links:
            seen_links.add(link)
            unique_results.append(r)

    return unique_results


# =========================================
# HYBRID SEARCH ENGINE (PARALLEL ⚡)
# =========================================

def hybrid_search(query, project_mode=True):

    final_query = build_project_query(query) if project_mode else query

    results = []

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [
            executor.submit(google_search, final_query),
            executor.submit(duckduckgo_search, final_query)
        ]

        for future in futures:
            try:
                data = future.result()
                if data:
                    results.extend(data)
            except:
                pass

    # remove duplicates
    unique_results = deduplicate(results)

    return {
        "query": query,
        "total_results": len(unique_results),
        "results": unique_results[:10]
    }