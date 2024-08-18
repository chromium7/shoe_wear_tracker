from django.urls import path

from . import views

app_name = "activities"

urlpatterns = [
    path('', views.index, name="index"),
    path('list/', views.strava_list, name="strava_list"),
    path('<int:id>/', views.details, name="details"),
    path('<int:id>/mark-no-photos/', views.mark_no_photos, name="mark_no_photos"),
    path('<int:id>/photos/add/', views.add_photo, name="add_photo"),
    path('<int:id>/photos/<int:photo_id>/edit/', views.edit_photo, name="edit_photo"),
]
