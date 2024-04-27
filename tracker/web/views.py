from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render

from libraries.strava import get_authorization_url
from tracker.core.utils import TrackerHttpRequest


@login_required
def index(request: TrackerHttpRequest) -> HttpResponse:
    if not hasattr(request.user, 'strava_profile'):
        strava_auth_url = get_authorization_url(request.user)
    else:
        strava_auth_url = None

    context = {
        'strava_auth_url': strava_auth_url,
    }
    return render(request, 'web/index.html', context=context)
