from groq import Groq
import os
import json
from dotenv import load_dotenv


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User

from .services import get_technology_info

load_dotenv()


# ---------------- LOGIN ----------------

def login_view(request):

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('/dashboard/')

        else:
            return render(request, "login.html", {
                "error": "Invalid credentials"
            })

    return render(request, "login.html")


# ---------------- HOME ----------------

def home(request):
    return render(request, "home.html")


# ---------------- AI CHAT ----------------

@csrf_exempt
@require_http_methods(["POST"])
def promentor_ai(request):

    try:
        data = json.loads(request.body)
        message = data.get("message", "")

        if not message:
            return JsonResponse({
                "error": "Message is required"
            }, status=400)

    except json.JSONDecodeError:
        return JsonResponse({
            "error": "Invalid JSON"
        }, status=400)


    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        return JsonResponse({
            "reply": "Groq API key not configured"
        }, status=500)


    try:
        client = Groq(api_key=api_key)

        system_prompt = """
You are ProMentor, an AI assistant inside the EngJect AI platform.

Your role:
- Help engineering students understand technology trends
- Suggest innovative engineering project ideas
- Provide guidance on technologies

Rules:
- Introduce yourself only if asked
- Keep responses short and structured
- If user asks about trending technologies → only list names
"""

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ]
        )

        reply_text = response.choices[0].message.content

        return JsonResponse({
            "reply": reply_text
        })

    except Exception as e:
        return JsonResponse({
            "reply": "AI error: " + str(e)
        })


# ---------------- SIGNUP ----------------

def signup_view(request):

    if request.method == "POST":

        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():

            return render(request, "signup.html", {
                "error": "Username already exists"
            })

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        user.save()

        return redirect("login")

    return render(request, "signup.html")


# ---------------- DASHBOARD ----------------

def dashboard(request):
    return render(request, "dashboard.html")


# ---------------- TECHNOLOGY DETAIL PAGE ----------------


def technology_detail(request, topic):

    tech = get_technology_info(topic)

    return render(request, "technology_detail.html", {"tech": tech})