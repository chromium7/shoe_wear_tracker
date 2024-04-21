from django.conf.urls import include
from django.urls import path

from . import views

app_name = "web"

urlpatterns = [
    path('', views.index, name="index"),
    path('activities/', include('tracker.web.activities.urls', namespace='activities')),
    path('auth/', include('tracker.web.auth.urls', namespace='auth')),
    path('shoes/', include('tracker.web.shoes.urls', namespace='shoes')),
]
