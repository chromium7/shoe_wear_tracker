from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from libraries.strava import get_athlete_shoes
from tracker.apps.photos.models import Photo
from tracker.core.utils import TrackerHttpRequest

from .forms import AddShoesForm, PhotoCategoryForm


@login_required
def index(request: TrackerHttpRequest) -> HttpResponse:
    shoes = request.user.shoes.select_related("brand")
    context = {
        "shoes": shoes,
        'selected_tab': 'index',
    }
    return render(request, "web/shoes/index.html", context)


@login_required
def details(request: TrackerHttpRequest, id: int) -> HttpResponse:
    shoes_qs = request.user.shoes.select_related("brand")
    shoes = get_object_or_404(shoes_qs, id=id)
    photo_prefetch = Prefetch('photos', Photo.objects.order_by('created')[:4], to_attr='prefetched_photos')
    categories = shoes.photo_categories.prefetch_related(photo_prefetch)
    context = {
        "shoe": shoes,
        "categories": categories,
        'selected_tab': 'details',
    }
    return render(request, "web/shoes/details.html", context)


@login_required
def activities(request: TrackerHttpRequest, id: int) -> HttpResponse:
    shoes = get_object_or_404(request.user.shoes, id=id)
    photos_prefetch = Prefetch('photos', Photo.objects.all()[:4], to_attr='prefetched_photos')
    activities = shoes.activities.prefetch_related(photos_prefetch).order_by('-created')

    context = {
        'shoe': shoes,
        'activities': activities,
        'selected_tab': 'activities',
    }
    return render(request, "web/shoes/activities.html", context)


@login_required
def add_photo_category(request: TrackerHttpRequest, id: int) -> HttpResponse:
    shoes = get_object_or_404(request.user.shoes, id=id)

    form = PhotoCategoryForm(data=request.POST or None, shoes=shoes)
    if form.is_valid():
        form.save()
        return redirect('web:shoes:details', shoes.id)

    context = {
        'title': shoes.name,
        'shoe': shoes,
        'form': form,
        'back_url': reverse('web:shoes:details', args=[shoes.id]),
    }
    return render(request, "web/form.html", context)


@login_required
def photo_category(request: TrackerHttpRequest, id: int, category_id: int) -> HttpResponse:
    shoes = get_object_or_404(request.user.shoes, id=id)
    category = get_object_or_404(shoes.photo_categories, id=category_id)

    photos = category.photos.order_by('created')
    context = {
        'shoe': shoes,
        'category': category,
        'photos': photos,
    }
    return render(request, "web/shoes/photo_category.html", context)


@login_required
def edit_photo_category(request: TrackerHttpRequest, id: int, category_id: int) -> HttpResponse:
    shoes = get_object_or_404(request.user.shoes, id=id)
    category = get_object_or_404(shoes.photo_categories, id=category_id)

    form = PhotoCategoryForm(data=request.POST or None, shoes=shoes, instance=category)
    if form.is_valid():
        form.save()
        return redirect('web:shoes:details', shoes.id)

    context = {
        'title': shoes.name,
        'shoe': shoes,
        'form': form,
        'back_url': reverse('web:shoes:details', args=[shoes.id]),
    }
    return render(request, "web/form.html", context)


@login_required
def strava_list(request: TrackerHttpRequest) -> HttpResponse:
    form = AddShoesForm(data=request.POST or None, user=request.user)
    if form.is_valid():
        shoes = form.save()
        messages.success(request, f'Shoes {shoes.name} has been added')

    registered_shoe_ids = set(request.user.shoes.values_list("strava_id", flat=True))
    strava_shoes = get_athlete_shoes(request.user)

    new_shoes = [shoe for shoe in strava_shoes if shoe.id not in registered_shoe_ids and not shoe.retired]
    context = {
        "new_shoes": new_shoes,
        'selected_tab': 'strava_list',
    }
    return render(request, "web/shoes/strava_list.html", context)
