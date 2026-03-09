import requests


def get_technology_info(topic):

    headers = {
        "User-Agent": "EngjectAI/1.0"
    }

    search_url = "https://en.wikipedia.org/w/api.php"

    # -----------------------------
    # STEP 1: SEARCH WIKIPEDIA PAGE
    # -----------------------------

    search_params = {
        "action": "query",
        "list": "search",
        "srsearch": topic,
        "format": "json"
    }

    response = requests.get(search_url, params=search_params, headers=headers)
    data = response.json()

    if not data["query"]["search"]:
        return None

    page_title = data["query"]["search"][0]["title"]

    # -----------------------------
    # STEP 2: FETCH FULL ARTICLE
    # -----------------------------

    content_params = {
        "action": "query",
        "prop": "extracts|pageimages",
        "titles": page_title,
        "explaintext": True,
        "format": "json",
        "pithumbsize": 500
    }

    content_response = requests.get(search_url, params=content_params, headers=headers)
    content_data = content_response.json()

    pages = content_data["query"]["pages"]
    page = list(pages.values())[0]

    text = page.get("extract", "")

    paragraphs = text.split("\n")

    # -----------------------------
    # STEP 3: STRUCTURED CONTENT
    # -----------------------------

    overview = paragraphs[0] if len(paragraphs) > 0 else ""

    history = paragraphs[1] if len(paragraphs) > 1 else ""

    applications = paragraphs[2] if len(paragraphs) > 2 else ""

    # -----------------------------
    # ADVANTAGES LIST
    # -----------------------------

    advantages = [
        f"{page_title} improves efficiency and automation in complex systems.",
        f"{page_title} enables faster data analysis and intelligent decision making.",
        f"{page_title} reduces human effort in repetitive and large-scale operations.",
        f"{page_title} increases productivity across industries like healthcare, finance and engineering.",
        f"{page_title} supports innovation and development of advanced technologies."
    ]

    # -----------------------------
    # CHALLENGES LIST
    # -----------------------------

    challenges = [
        f"High computational and infrastructure requirements for {page_title}.",
        "Ethical concerns such as bias, privacy, and responsible usage.",
        "Security risks when deployed in critical systems.",
        "High development and implementation cost.",
        "Requires skilled engineers and researchers."
    ]

    # -----------------------------
    # FUTURE SCOPE
    # -----------------------------

    future_scope = [
        f"{page_title} will continue evolving with AI, automation, and advanced computing.",
        f"Future developments of {page_title} will enable smarter intelligent systems.",
        "Integration with robotics, IoT and cloud computing will expand its applications.",
        "Industries will increasingly adopt this technology for automation and decision-making.",
        "Research in this field will drive next-generation innovations."
    ]

    # -----------------------------
    # RESEARCH PAPERS (STATIC DEMO)
    # -----------------------------

    papers = [
        {
            "title": f"Recent Advances in {page_title}",
            "link": "https://arxiv.org/"
        },
        {
            "title": f"Applications of {page_title} in Modern Engineering",
            "link": "https://arxiv.org/"
        },
        {
            "title": f"{page_title} for Intelligent Systems",
            "link": "https://arxiv.org/"
        }
    ]

    # -----------------------------
    # ENGINEERING PROJECT IDEAS
    # -----------------------------

    projects = [
        f"{page_title} based intelligent monitoring system",
        f"{page_title} predictive analytics platform",
        f"{page_title} automated decision support system",
        f"{page_title} smart recommendation engine",
        f"{page_title} real-time data analysis dashboard"
    ]

    # -----------------------------
    # FINAL RETURN
    # -----------------------------

    return {
        "title": page.get("title"),
        "image": page.get("thumbnail", {}).get("source"),
        "overview": overview,
        "history": history,
        "applications": applications,
        "advantages": advantages,
        "challenges": challenges,
        "future_scope": future_scope,
        "papers": papers,
        "projects": projects
    }