from django.urls import path

from . import views

app_name = "shoes"

urlpatterns = [
    path('', views.index, name="index"),
    path('<int:id>/', views.details, name="details"),
]
