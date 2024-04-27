from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from libraries.strava import get_athlete_shoes
from tracker.core.utils import TrackerHttpRequest


@login_required
def index(request: TrackerHttpRequest) -> HttpResponse:
    shoes = request.user.shoes.select_related('brand')
    context = {
        'shoes': shoes,
    }
    return render(request, 'web/shoes/index.html', context)


@login_required
def details(request: TrackerHttpRequest, id: int) -> HttpResponse:
    shoes_qs = request.user.shoes.select_related('brand')
    shoes = get_object_or_404(shoes_qs, id=id)
    context = {
        'shoes': shoes,
    }
    return render(request, 'web/shoes/details.html', context)


@login_required
def strava_list(request: TrackerHttpRequest) -> HttpResponse:
    registered_shoe_ids = set(request.user.shoes.values_list('strava_id', flat=True))
    strava_shoes = get_athlete_shoes(request.user)

    new_shoes = [shoe for shoe in strava_shoes if shoe.id not in registered_shoe_ids]
    context = {
        'new_shoes': new_shoes,
    }
    return render(request, 'web/shoes/strava_list.html', context)
