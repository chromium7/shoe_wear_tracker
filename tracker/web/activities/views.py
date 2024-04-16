from collections import defaultdict

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from tracker.core.utils import TrackerHttpRequest


@login_required
def index(request: TrackerHttpRequest) -> HttpResponse:
    activities = request.user.activities.all()
    context = {
        'activities': activities,
    }
    return render('web/activities/index.html', context)


@login_required
def details(request: TrackerHttpRequest, id: int) -> HttpResponse:
    activity_qs = request.user.activities.select_related("shoes").prefetch_related(
        "photo_categories", "photos"
    )
    activity = get_object_or_404(activity_qs, id=id, user_id=request.user.id)

    category_mapping = {category.id for category in activity.photo_categories.all()}
    photos_by_category = defaultdict(list)
    for photo in activity.photos.all():
        category = category_mapping.get(photo.category_id)
        photos_by_category[category].append(photo)

    context = {
        'activity': activity,
        'photo_by_categories': photos_by_category,
    }
    return render('web/activities/details.html', context)
