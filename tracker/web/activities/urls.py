from django.urls import path

from . import views

app_name = "activities"

urlpatterns = [
    path('', views.index, name="index"),
    path('<int:id>/', views.details, name="details"),
]
