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

from .services import get_technology_info
from .search_service import hybrid_search

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")


# =========================================================
# HOME
# =========================================================

def home(request):
    return render(request, "home.html")


# =========================================================
# LOGIN
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


# =========================================================
# LOGOUT
# =========================================================

def logout_view(request):
    logout(request)
    return redirect("/")


# =========================================================
# SIGNUP
# =========================================================

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
# DASHBOARD – GLOBAL TECHNOLOGY TRENDS
# =========================================================

def dashboard(request):

    trends = []

    # -------- GOOGLE TRENDS --------
    try:
        pytrends = TrendReq()
        google_trends = pytrends.trending_searches(pn="united_states")
        trends += google_trends[0].tolist()
    except Exception:
        pass

    # -------- WIKIPEDIA TRENDING --------
    try:

        wiki_url = "https://wikimedia.org/api/rest_v1/metrics/pageviews/top/en.wikipedia/all-access/1/day/latest"

        res = requests.get(wiki_url, timeout=6)

        if res.status_code == 200:

            data = res.json()
            articles = data["items"][0]["articles"]

            for article in articles[:20]:
                trends.append(article["article"].replace("_", " "))

    except Exception:
        pass


    # -------- FALLBACK --------
    if not trends:

        trends = [
            "Artificial Intelligence",
            "Quantum Computing",
            "Cybersecurity",
            "Blockchain",
            "Climate Technology",
            "SpaceX"
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

        except Exception:
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
# TECHNOLOGY DETAIL PAGE
# =========================================================

def technology_detail(request, topic):

    tech = get_technology_info(topic)

    if not tech:
        return render(request, "technology_detail.html", {
            "tech": {
                "title": topic,
                "overview": "No information available.",
            }
        })

    return render(request, "technology_detail.html", {
        "tech": tech
    })


# =========================================================
# PROMENTOR AI
# =========================================================

@csrf_exempt
@require_http_methods(["POST"])
def promentor_ai(request):

    try:

        data = json.loads(request.body)
        message = data.get("message")

        if not message:
            return JsonResponse({
                "error": "Message required"
            }, status=400)

    except json.JSONDecodeError:
        return JsonResponse({
            "error": "Invalid JSON"
        }, status=400)


    if not GROQ_API_KEY:
        return JsonResponse({
            "reply": "AI service unavailable."
        })


    try:

        client = Groq(api_key=GROQ_API_KEY)

        system_prompt = """
You are ProMentor AI inside the EngJect engineering platform.

Rules:
• Introduce yourself in short.
• Answer directly.
• Keep responses short and structured.

When user asks about a technology respond with:

Overview
Key Applications
Current Developments
Engineering Opportunities

If user asks for project ideas → give 5 concise engineering project ideas.
"""

        response = client.chat.completions.create(

            model="llama-3.1-8b-instant",

            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ]

        )

        reply = response.choices[0].message.content

        return JsonResponse({"reply": reply})

    except Exception as e:

        return JsonResponse({
            "reply": f"AI error: {str(e)}"
        })


# =========================================================
# SEARCH ENGINE
# =========================================================

@csrf_exempt
@require_http_methods(["POST"])
def search_engine(request):

    try:

        data = json.loads(request.body)

        query = data.get("query")

        if not query:
            return JsonResponse({
                "error": "Query required"
            }, status=400)

        search_data = hybrid_search(query)

        return JsonResponse({
            "results": search_data.get("results", [])
        })

    except Exception as e:

        return JsonResponse({
            "error": str(e)
        }, status=500)
    
TECH_IMAGES = {
    "Artificial Intelligence": "https://images.unsplash.com/photo-1677442136019-21780ecad995",
    "Cybersecurity": "https://images.unsplash.com/photo-1550751827-4bd374c3f58b",
    "Quantum Computing": "https://images.unsplash.com/photo-1635070041078-e363dbe005cb",
    "Blockchain": "https://images.unsplash.com/photo-1639762681485-074b7f938ba0",
    "SpaceX": "https://images.unsplash.com/photo-1517976487492-5750f3195933",
    "Climate Technology": "https://images.unsplash.com/photo-1509395176047-4a66953fd231"
}