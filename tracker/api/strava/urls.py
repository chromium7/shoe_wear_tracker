from django.urls import path

from . import views

app_name = "strava"

urlpatterns = [
    path("notification", views.Notification.as_view(), name="notification"),
    path("authorized", views.Authorized.as_view(), name="authorized"),
]
