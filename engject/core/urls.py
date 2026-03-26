from django.urls import path
from . import views

urlpatterns = [

    # ===============================
    # HOME
    # ===============================
    path("", views.home, name="home"),


    # ===============================
    # DASHBOARD
    # ===============================
    path("dashboard/", views.dashboard, name="dashboard"),


    # ===============================
    # AUTHENTICATION
    # ===============================
    path("login/", views.login_view, name="login"),
    path("signup/", views.signup_view, name="signup"),
    path("logout/", views.logout_view, name="logout"),


    # ===============================
    # MAIN FEATURES
    # ===============================
    path("promentor-ai/", views.promentor_page, name="promentor_page"),
    path("trends/", views.trends, name="trends"),
    path("project-news/", views.project_news, name="project_news"),


    # ===============================
    # PROJECTS (UI PAGES)
    # ===============================
    path("projects/", views.projects_hub, name="projects_hub"),
    path("projects/github/", views.github_projects, name="github_projects"),
    path("projects/gov/<str:source>/", views.gov_projects, name="gov_projects"),

    # (Future-ready placeholders)


    # ===============================
    # PROJECT DETAIL
    # ===============================
    path(
        "project/<str:owner>/<str:repo>/",
        views.project_detail,
        name="project_detail"
    ),


    # ===============================
    # TECHNOLOGY DETAILS
    # ===============================
    path(
        "technology/<str:topic>/",
        views.technology_detail,
        name="technology_detail"
    ),


    # ===============================
    # 🔥 UNIFIED SEARCH API (IMPORTANT)
    # ===============================
    path(
        "api/search/",
        views.search_projects,   # UPDATED NAME
        name="search_projects"
    ),


    # ===============================
    # 🔥 PLATFORM-SPECIFIC APIs
    # ===============================
    path("api/search/github/", views.search_github, name="search_github"),
    path("api/search/web/", views.search_web, name="search_web"),
    path("api/search/ai/", views.search_ai, name="search_ai"),
    path("api/search/gov/", views.search_gov_projects, name="search_gov_projects"),

    # future


    # ===============================
    # PROMENTOR AI API
    # ===============================
    path(
        "api/promentor/",
        views.promentor_api,
        name="promentor_api"
    ),


    # ===============================
    # NEWS
    # ===============================
    path(
        "news-detail/<str:topic>/",
        views.news_detail,
        name="news_detail"
    ),
]