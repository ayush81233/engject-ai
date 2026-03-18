import requests
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()


# =========================================
# AI PROJECT IDEAS GENERATOR
# =========================================

def generate_project_ideas(topic):

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        return []

    try:

        client = Groq(api_key=api_key)

        prompt = f"""
Generate 5 innovative engineering project ideas related to {topic}.
Keep each idea short (1 sentence).
Focus on real engineering systems or prototypes.
"""

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        text = response.choices[0].message.content

        ideas = [
            line.strip("-• ")
            for line in text.split("\n")
            if line.strip()
        ]

        return ideas[:5]

    except Exception as e:

        print("AI project idea generation failed:", e)

        return []


# =========================================
# GOOGLE SOURCES
# =========================================

def get_sources(topic):

    try:

        url = f"https://www.googleapis.com/customsearch/v1"

        params = {
            "key": os.getenv("GOOGLE_API_KEY"),
            "cx": os.getenv("GOOGLE_CSE_ID"),
            "q": topic,
            "num": 5
        }

        res = requests.get(url, params=params, timeout=8)

        if res.status_code != 200:
            return []

        data = res.json()

        sources = []

        for item in data.get("items", []):

            sources.append({
                "title": item.get("title"),
                "link": item.get("link")
            })

        return sources

    except Exception:

        return []


# =========================================
# WIKIPEDIA TECHNOLOGY INFO
# =========================================

def get_technology_info(topic):

    headers = {
        "User-Agent": "EngjectAI/1.0"
    }

    try:

        search_url = "https://en.wikipedia.org/w/api.php"

        # -----------------------------
        # FIND PAGE
        # -----------------------------

        search_params = {
            "action": "query",
            "list": "search",
            "srsearch": topic,
            "format": "json"
        }

        response = requests.get(
            search_url,
            params=search_params,
            headers=headers,
            timeout=8
        )

        data = response.json()

        if not data.get("query", {}).get("search"):
            return None

        page_title = data["query"]["search"][0]["title"]

        # -----------------------------
        # FETCH CONTENT
        # -----------------------------

        content_params = {
            "action": "query",
            "prop": "extracts|pageimages",
            "titles": page_title,
            "explaintext": True,
            "format": "json",
            "pithumbsize": 600
        }

        content_response = requests.get(
            search_url,
            params=content_params,
            headers=headers,
            timeout=8
        )

        content_data = content_response.json()

        pages = content_data["query"]["pages"]
        page = list(pages.values())[0]

        text = page.get("extract", "")

        paragraphs = [
            p.strip()
            for p in text.split("\n")
            if len(p.strip()) > 60
        ]

        overview = paragraphs[0] if len(paragraphs) > 0 else ""
        history = paragraphs[1] if len(paragraphs) > 1 else ""
        applications = paragraphs[2] if len(paragraphs) > 2 else ""

        advantages = paragraphs[3:6] if len(paragraphs) > 5 else []
        challenges = paragraphs[6:9] if len(paragraphs) > 8 else []
        future_scope = paragraphs[9:12] if len(paragraphs) > 11 else []

        # -----------------------------
        # IMAGE
        # -----------------------------

        image = page.get("thumbnail", {}).get("source")

        if not image:
            image = f"https://source.unsplash.com/800x400/?technology,{topic}"

        # -----------------------------
        # RESEARCH PAPERS
        # -----------------------------

        papers = [
            {
                "title": f"Research papers about {page_title}",
                "link": f"https://arxiv.org/search/?query={page_title}&searchtype=all"
            }
        ]

        # -----------------------------
        # AI PROJECT IDEAS
        # -----------------------------

        projects = generate_project_ideas(page_title)

        # -----------------------------
        # SOURCES
        # -----------------------------

        sources = get_sources(page_title)

        # -----------------------------
        # FINAL DATA
        # -----------------------------
        current_situation = get_current_situation(page_title)

        return {
    "title": page_title,
    "image": image,
    "overview": overview,
    "history": history,
    "applications": applications,
    "advantages": advantages,
    "challenges": challenges,
    "future_scope": future_scope,
    "papers": papers,
    "projects": projects,
    "sources": sources,
    "current_situation": current_situation
}

    except Exception as e:

        print("Wikipedia fetch failed:", e)

        return None

def get_current_situation(topic):

    try:

        url = "https://newsapi.org/v2/everything"

        params = {
            "q": topic,
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": 5,
            "apiKey": os.getenv("NEWS_API_KEY")
        }

        res = requests.get(url, params=params, timeout=8)

        if res.status_code != 200:
            return []

        data = res.json()

        news = []

        for article in data.get("articles", []):

            news.append({
                "title": article["title"],
                "description": article["description"],
                "link": article["url"],
                "source": article["source"]["name"]
            })

        return news

    except Exception:
        return []