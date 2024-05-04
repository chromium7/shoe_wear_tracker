from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as django_login, logout as django_logout
from django.http import HttpResponse
from django.shortcuts import redirect, render

from libraries.strava import get_authorization_url
from tracker.core.utils import TrackerHttpRequest


def sign_in(request: TrackerHttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        messages.success(request, 'Already logged in')
        return redirect('web:activities:index')

    form = AuthenticationForm(data=request.POST or None)
    if form.is_valid():
        user = form.get_user()
        django_login(request, user)

        if not hasattr(user, 'strava_profile'):
            url = get_authorization_url(user)
            return redirect(url)

        return redirect('web:activities:index')

    context = {
        'form': form,
        'button_name': 'Sign In',
    }
    return render(request, 'web/form.html', context)


def sign_out(request: TrackerHttpRequest) -> HttpResponse:
    django_logout(request)
    return redirect('web:auth:sign_in')
