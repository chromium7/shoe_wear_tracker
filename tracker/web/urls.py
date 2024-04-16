from django.conf.urls import include
from django.urls import path

app_name = "web"

urlpatterns = [
    path('auth/', include('tracker.web.auth.urls', namespace='auth')),
    path('shoes/', include('tracker.web.shoes.urls', namespace='shoes')),
    path('', include('tracker.web.activities.urls', namespace='activities')),
]
