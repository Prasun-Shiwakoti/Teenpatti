from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="index"),
    path("username_validate", views.validate_usernames),
]
