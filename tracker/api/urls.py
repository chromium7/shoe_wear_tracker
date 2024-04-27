from django.conf.urls import include
from django.urls import path

from .views import Ping

app_name = "api"

urlpatterns = [
    path('ping', Ping.as_view(), name="ping"),
    path('strava/', include('tracker.api.strava.urls', namespace='strava')),
]
