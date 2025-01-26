from django.urls import path

from . import views

app_name = "shoes"

urlpatterns = [
    path("photo-categories/", views.photo_categories, name="photo_categories"),
    path("photos/", views.photos, name="photos"),
]
