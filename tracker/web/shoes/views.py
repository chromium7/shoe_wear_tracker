from collections import defaultdict

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

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
