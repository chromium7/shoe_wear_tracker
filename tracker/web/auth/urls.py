from django.urls import path

from .views import dummy

app_name = "auth"

urlpatterns = [
    path('sign-in', dummy, name="sign_in"),
    path('sign-out', dummy, name="sign_out"),
]
