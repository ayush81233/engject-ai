import os
import json
import random
import requests
import urllib.parse

from dotenv import load_dotenv
from groq import Groq
from pytrends.request import TrendReq

from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

# =========================
# SERVICES IMPORTS
# =========================
from .services import get_technology_info, generate_project_ideas
from .search_service import hybrid_search
from .github_service import fetch_github_repos, get_repo_details

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")


# =========================================================
# HOME
# =========================================================
def home(request):
    return render(request, "home.html")


# =========================================================
# AUTHENTICATION
# =========================================================
def login_view(request):

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect("/dashboard/")

        return render(request, "login.html", {
            "error": "Invalid username or password"
        })

    return render(request, "login.html")


def logout_view(request):
    logout(request)
    return redirect("/")


def signup_view(request):

    if request.method == "POST":

        username = request.POST.get("username")
        email = request.POST.get("email")

        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if password1 != password2:
            return render(request, "signup.html", {
                "error": "Passwords do not match"
            })

        if User.objects.filter(username=username).exists():
            return render(request, "signup.html", {
                "error": "Username already exists"
            })

        User.objects.create_user(
            username=username,
            email=email,
            password=password1
        )

        return redirect("/login/")

    return render(request, "signup.html")


# =========================================================
# DASHBOARD – GLOBAL TRENDS
# =========================================================
def dashboard(request):

    trends = []

    try:
        pytrends = TrendReq()
        google_trends = pytrends.trending_searches(pn="united_states")
        trends += google_trends[0].tolist()
    except:
        pass

    try:
        wiki_url = "https://wikimedia.org/api/rest_v1/metrics/pageviews/top/en.wikipedia/all-access/1/day/latest"
        res = requests.get(wiki_url, timeout=6)

        if res.status_code == 200:
            data = res.json()
            articles = data["items"][0]["articles"]

            for article in articles[:20]:
                trends.append(article["article"].replace("_", " "))

    except:
        pass

    if not trends:
        trends = [
            "Artificial Intelligence",
            "Quantum Computing",
            "Cybersecurity",
            "Blockchain",
            "Climate Technology"
        ]

    trends = list(set(trends))
    random.shuffle(trends)

    selected = trends[:6]

    tech_data = []

    for topic in selected:

        description = "Trending worldwide right now."

        try:
            encoded = urllib.parse.quote(topic)
            wiki_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}"

            res = requests.get(wiki_url, timeout=5)

            if res.status_code == 200:
                data = res.json()
                extract = data.get("extract")

                if extract:
                    description = extract.split(".")[0] + "."

        except:
            pass

        tech_data.append({
            "title": topic,
            "description": description,
            "image": TECH_IMAGES.get(topic, "https://source.unsplash.com/600x400/?technology")
        })

    return render(request, "dashboard.html", {
        "tech_data": tech_data
    })


# =========================================================
# TECHNOLOGY DETAIL
# =========================================================
def technology_detail(request, topic):

    tech = get_technology_info(topic)

    if not tech:
        return render(request, "technology_detail.html", {
            "tech": {"title": topic, "overview": "No info available"}
        })

    return render(request, "technology_detail.html", {"tech": tech})


# =========================================================
# PROMENTOR AI
# =========================================================
def promentor_page(request):
    return render(request, "promentor.html")


@csrf_exempt
@require_http_methods(["POST"])
def promentor_api(request):

    try:
        data = json.loads(request.body)
        message = data.get("message")

        if not message:
            return JsonResponse({"error": "Message required"}, status=400)

    except:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    if not GROQ_API_KEY:
        return JsonResponse({"reply": "AI unavailable"})

    try:
        client = Groq(api_key=GROQ_API_KEY)

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are an engineering mentor AI."},
                {"role": "user", "content": message}
            ]
        )

        return JsonResponse({
            "reply": response.choices[0].message.content
        })

    except Exception as e:
        return JsonResponse({"error": str(e)})


# =========================================================
# 🔥 UNIFIED SEARCH ENGINE
# =========================================================
@csrf_exempt
@require_http_methods(["POST"])
def search_projects(request):

    data = json.loads(request.body)
    query = data.get("query")

    tech = get_technology_info(query)

    # 🔥 ADD AI IDEAS BACK
    ai_ideas = generate_project_ideas(query)

    return JsonResponse({
        "data": tech,
        "ai": ai_ideas   # ✅ NEW
    })


# =========================================================
# PLATFORM APIs
# =========================================================
@csrf_exempt
@require_http_methods(["POST"])
def search_github(request):
    data = json.loads(request.body)
    return JsonResponse({
        "results": fetch_github_repos(data.get("query"))
    })


@csrf_exempt
@require_http_methods(["POST"])
def search_web(request):
    data = json.loads(request.body)
    project_mode = data.get("project_mode", False)
    return JsonResponse({
        "results": hybrid_search(data.get("query"), project_mode=project_mode).get("results", [])
    })


@csrf_exempt
@require_http_methods(["POST"])
def search_ai(request):
    data = json.loads(request.body)
    return JsonResponse({
        "results": generate_project_ideas(data.get("query"))
    })


# =========================================================
# PROJECTS (HUB)
# =========================================================
def projects_hub(request):
    return render(request, "projects_hub.html")


# =========================================================
# PROJECTS (GITHUB UI)
# =========================================================
def github_projects(request):

    query = request.GET.get("q", "machine learning")
    repos = fetch_github_repos(query)

    return render(request, "github_projects.html", {
        "repos": repos,
        "query": query
    })


def project_detail(request, owner, repo):

    data = get_repo_details(owner, repo)

    if not data:
        return render(request, "error.html")

    return render(request, "project_detail.html", {"repo": data})


# =========================================================
# PROJECTS (GOV UI)
# =========================================================
def gov_projects(request, source):
    # source will be 'kscst' or 'sih'
    return render(request, "gov_projects.html", {"source": source.upper()})

@csrf_exempt
@require_http_methods(["POST"])
def search_gov_projects(request):
    try:
        data = json.loads(request.body)
        query = data.get("query")
        source = data.get("source", "SIH")

        client = Groq(api_key=GROQ_API_KEY)
        prompt = f"""You are an API. Return a JSON array of exactly 4 hypothetical or real student technical projects related to '{query}' under the auspices of {source} (Smart India Hackathon or Karnataka State Council for Science and Technology).
Each object must have these exactly:
- "title": Short realistic project title
- "problem_statement": A clear 1-2 sentence problem statement definition being solved.
- "overview": A concise paragraph explaining the technical solution.
- "source": "{source}"
- "link": "https://{source.lower()}.gov.in/portal/projects/view"

Output strictly and ONLY a valid JSON array of objects. Do not wrap in markdown or backticks."""

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        content = response.choices[0].message.content
        import re
        match = re.search(r'\[.*\]', content, re.DOTALL)
        if match:
            projects = json.loads(match.group(0))
        else:
            projects = json.loads(content)

        return JsonResponse({"results": projects})
    except Exception as e:
        return JsonResponse({"error": str(e), "results": []})


# =========================================================
# NEWS
# =========================================================
def news_detail(request, topic):
    data = get_technology_info(topic)
    return render(request, "news_detail.html", {"data": data})


# =========================================================
# STATIC IMAGES
# =========================================================
TECH_IMAGES = {
    "Artificial Intelligence": "https://images.unsplash.com/photo-1677442136019-21780ecad995",
    "Cybersecurity": "https://images.unsplash.com/photo-1550751827-4bd374c3f58b",
    "Quantum Computing": "https://images.unsplash.com/photo-1635070041078-e363dbe005cb",
    "Blockchain": "https://images.unsplash.com/photo-1639762681485-074b7f938ba0",
}
def trends(request):
    return render(request, "trends.html")

def project_news(request):
    return render(request, "project_news.html")

