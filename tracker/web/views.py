from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render

from tracker.core.utils import TrackerHttpRequest


@login_required
def index(request: TrackerHttpRequest) -> HttpResponse:
    return render(request, 'web/index.html')
