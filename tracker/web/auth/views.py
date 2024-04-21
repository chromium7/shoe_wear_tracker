from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as django_login, logout as django_logout
from django.http import HttpResponse
from django.shortcuts import redirect, render

from tracker.core.utils import TrackerHttpRequest


def sign_in(request: TrackerHttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        messages.success(request, 'Already logged in')
        return redirect('web:activities:index')

    form = AuthenticationForm(data=request.POST or None)
    if form.is_valid():
        user = form.get_user()
        django_login(request, user)
        return redirect('web:activities:index')

    context = {
        'form': form,
    }
    return render(request, 'web/auth/sign_in.html', context)


def sign_out(request: TrackerHttpRequest) -> HttpResponse:
    django_logout(request)
    return redirect('web:auth:sign_in')
