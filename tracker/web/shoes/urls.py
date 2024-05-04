from django.urls import path

from . import views

app_name = "shoes"

urlpatterns = [
    path('', views.index, name="index"),
    path('list/', views.strava_list, name="strava_list"),
    path('<int:id>/', views.details, name="details"),
    path('<int:id>/photo-category/add/', views.add_photo_category, name="add_photo_category"),
    path('<int:id>/photo-category/<int:category_id>/', views.photo_category, name="photo_category"),
    path('<int:id>/photo-category/<int:category_id>/edit/', views.edit_photo_category, name="edit_photo_category"),
    path('<int:id>/activites/', views.activities, name="activities"),
]
