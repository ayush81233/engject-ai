import requests
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

HEADERS = {
    "User-Agent": "EngjectAI/1.0"
}


# =========================================
# AI PROJECT IDEAS GENERATOR (IMPROVED)
# =========================================

def generate_project_ideas(topic):

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        return []

    try:
        client = Groq(api_key=api_key)

        prompt = f"""
Generate 5 innovative engineering project ideas related to {topic}.
Each idea should be:
- 1 line
- Practical & buildable
- Unique (not generic)

Return only bullet points.
"""

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )

        text = response.choices[0].message.content

        ideas = [
            line.strip("-• ").strip()
            for line in text.split("\n")
            if len(line.strip()) > 10
        ]

        return ideas[:5]

    except Exception as e:
        print("AI project idea generation failed:", e)
        return []


# =========================================
# GOOGLE SOURCES (IMPROVED)
# =========================================

def get_sources(topic):

    try:
        url = "https://www.googleapis.com/customsearch/v1"

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
                "link": item.get("link"),
                "source": "Google"
            })

        return sources

    except Exception as e:
        print("Source fetch failed:", e)
        return []


# =========================================
# WIKIPEDIA TECHNOLOGY INFO (UPGRADED)
# =========================================

def get_technology_info(topic):

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
            headers=HEADERS,
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
            headers=HEADERS,
            timeout=8
        )

        content_data = content_response.json()
        pages = content_data["query"]["pages"]
        page = list(pages.values())[0]

        text = page.get("extract", "")

        paragraphs = [
            p.strip()
            for p in text.split("\n")
            if len(p.strip()) > 80
        ]

        # safer extraction
        overview = paragraphs[0] if len(paragraphs) > 0 else ""
        applications = paragraphs[1] if len(paragraphs) > 1 else ""

        advantages = paragraphs[2:5] if len(paragraphs) > 4 else []
        challenges = paragraphs[5:8] if len(paragraphs) > 7 else []
        future_scope = paragraphs[8:11] if len(paragraphs) > 10 else []

        # -----------------------------
        # IMAGE
        # -----------------------------
        image = page.get("thumbnail", {}).get("source")

        if not image:
            image = f"https://source.unsplash.com/800x400/?technology,{topic}"

        # -----------------------------
        # RESEARCH PAPERS
        # -----------------------------
        papers = [{
            "title": f"Research papers about {page_title}",
            "link": f"https://arxiv.org/search/?query={page_title}&searchtype=all"
        }]

        # -----------------------------
        # AI PROJECT IDEAS
        # -----------------------------
        projects = generate_project_ideas(page_title)

        # -----------------------------
        # SOURCES
        # -----------------------------
        sources = get_sources(page_title)

        # -----------------------------
        # CURRENT SITUATION (NEWS)
        # -----------------------------
        current_situation = get_current_situation(page_title)

        # -----------------------------
        # FINAL RESPONSE
        # -----------------------------
        return {
            "title": page_title,
            "image": image,
            "overview": overview,
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


# =========================================
# CURRENT SITUATION (NEWS API)
# =========================================

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
                "title": article.get("title"),
                "description": article.get("description"),
                "link": article.get("url"),
                "source": article.get("source", {}).get("name")
            })

        return news

    except Exception as e:
        print("News fetch failed:", e)
        return []