from django.urls import path

from . import views

app_name = "shoes"

urlpatterns = [
    path("shoes/photo-categories/", views.photo_categories, name="photo_categories"),
    path("shoes/photos/", views.photos, name="photos"),
]
