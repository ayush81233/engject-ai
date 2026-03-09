from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"), 

    path("dashboard/", views.dashboard, name="dashboard"),

    path("login/", views.login_view, name="login"),

    path("signup/", views.signup_view, name="signup"),

    path("promentor-ai/", views.promentor_ai, name="promentor_ai"),

    path("technology/<str:topic>/", views.technology_detail, name="technology_detail"),


]