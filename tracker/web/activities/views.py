from collections import defaultdict
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from django.forms import formset_factory
from django.http import HttpResponse
from django.urls import reverse
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect, render

from libraries.strava import get_athlete_activities
from tracker.apps.photos.models import Photo
from tracker.core.utils import TrackerHttpRequest, Paginator

from .forms import ActivityFilterForm, ActivityPhotoForm, AddActivityForm, BaseActivityPhotoFormSet


@login_required
def index(request: TrackerHttpRequest) -> HttpResponse:
    photos_prefetch = Prefetch('photos', Photo.objects.order_by('category_id')[:4], to_attr='prefetched_photos')
    activities_qs = request.user.activities.prefetch_related(photos_prefetch).order_by('-created')

    form = ActivityFilterForm(data=request.GET)
    if form.is_valid():
        activities_qs = form.filter_activities(activity_qs=activities_qs)
        page = form.cleaned_data['page']
        selected_tab = form.get_selected_tab()
    else:
        page = 1
        selected_tab = 'index'

    paginator = Paginator(activities_qs, page, 10)
    context = {
        'activities': paginator.objects,
        'paginator': paginator,
        'selected_tab': selected_tab,
    }
    return render(request, 'web/activities/index.html', context)


@login_required
def details(request: TrackerHttpRequest, id: int) -> HttpResponse:
    activity_qs = request.user.activities.select_related('shoes').prefetch_related('photos')
    activity = get_object_or_404(activity_qs, id=id, user_id=request.user.id)

    category_mapping = {category.id: category for category in activity.shoes.photo_categories.all()}
    photos_by_category = defaultdict(list)
    for photo in activity.photos.all():
        category = category_mapping.get(photo.category_id)
        photos_by_category[category].append(photo)

    context = {
        'activity': activity,
        'photo_by_categories': dict(photos_by_category),
    }
    return render(request, 'web/activities/details.html', context)


@login_required
def add_photo(request: TrackerHttpRequest, id: int) -> HttpResponse:
    activity = get_object_or_404(request.user.activities.select_related('shoes'), id=id, user_id=request.user.id)
    photo_categories = activity.shoes.photo_categories.all()

    initials = [{'category': category.id} for category in photo_categories]

    ActivityPhotoFormSet = formset_factory(form=ActivityPhotoForm, formset=BaseActivityPhotoFormSet, extra=0)
    formset = ActivityPhotoFormSet(
        data=request.POST or None,
        files=request.FILES or None,
        activity=activity,
        initial=initials,
        form_kwargs={'shoes': activity.shoes},
    )
    if formset.is_valid():
        for form in formset.forms:
            form.save()
        return redirect('web:activities:details', activity.id)

    context = {
        'title': f'Add photo to {activity.name}',
        'formset': formset,
        'back_url': reverse('web:activities:details', args=[activity.id]),
    }
    return render(request, 'web/form.html', context)


@login_required
def edit_photo(request: TrackerHttpRequest, id: int, photo_id: int) -> HttpResponse:
    activity = get_object_or_404(request.user.activities, id=id)
    photo = get_object_or_404(activity.photos, id=photo_id)

    form = ActivityPhotoForm(
        data=request.POST or None, files=request.FILES or None, shoes=activity.shoes, instance=photo
    )
    if form.is_valid():
        form.save()
        return redirect('web:activities:details', activity.id)

    context = {
        'title': f'Edit photo {activity.name}',
        'form': form,
        'back_url': reverse('web:activities:details', args=[activity.id]),
    }
    return render(request, 'web/form.html', context)


@login_required
def strava_list(request: TrackerHttpRequest) -> HttpResponse:
    form = AddActivityForm(data=request.POST or None, user=request.user)
    if form.is_valid():
        activity = form.save()
        messages.success(request, f'Activity {activity.name} has been added')
        return redirect('web:activities:details', activity.id)

    after = timezone.localtime() - timedelta(days=30)
    registered_activity_ids = set(
        request.user.activities.filter(created__gte=after).values_list('strava_id', flat=True)
    )
    active_shoes_mapping = {shoe.strava_id: shoe for shoe in request.user.shoes.filter(retired_at=None)}
    # Get activities in the past 30 days
    strava_activities = get_athlete_activities(request.user, after=after)

    new_activities = []
    for activity in strava_activities:
        shoes = active_shoes_mapping.get(activity.shoes_id)
        if str(activity.id) not in registered_activity_ids and shoes:
            activity.shoes = shoes
            new_activities.append(activity)

    context = {
        'form': form,
        'new_activities': new_activities,
        'selected_tab': 'strava_list',
    }
    return render(request, 'web/activities/strava_list.html', context)
