from django.urls import path

from . import views

app_name = "activities"

urlpatterns = [
    path('', views.index, name="index"),
    path('<int:id>/', views.details, name="details"),
    path('<int:id>/photos/add', views.add_photo, name="add_photo"),
]
