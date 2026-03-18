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
    path("promentor-ai/", views.promentor_ai, name="promentor_ai"),


    # ===============================
    # TECHNOLOGY DETAILS
    # ===============================
    path(
        "technology/<str:topic>/",
        views.technology_detail,
        name="technology_detail"
    ),


    # ===============================
    # SEARCH API
    # ===============================
    path(
        "api/search/",
        views.search_engine,
        name="search_engine"
    ),


    # ===============================
    # PROMENTOR AI API
    # ===============================
    path(
        "api/promentor/",
        views.promentor_ai,
        name="promentor_ai"
    ),

]