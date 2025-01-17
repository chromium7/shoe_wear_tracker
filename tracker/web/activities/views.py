from collections import defaultdict

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from django.forms import formset_factory
from django.http import HttpResponse
from django.urls import reverse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from libraries.strava import STRAVA_SPORT_TYPES
from tracker.apps.activities.models import Activity
from tracker.apps.activities.utils import get_unregistered_strava_activities
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
    activity = get_object_or_404(request.user.activities.select_related('shoes'), id=id)
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

    new_activities = get_unregistered_strava_activities(request.user)
    context = {
        'form': form,
        'new_activities': new_activities,
        'selected_tab': 'strava_list',
    }
    return render(request, 'web/activities/strava_list.html', context)


@require_POST
@login_required
def bulk_add(request: TrackerHttpRequest) -> HttpResponse:
    new_activities = get_unregistered_strava_activities(request.user)

    # Make sure shoe distance is correct
    shoes = {activity.shoes for activity in new_activities}
    for shoe in shoes:
        shoe.recalculate_distance_covered()

    shoe_distance_mapping = {shoe: shoe.distance_covered for shoe in shoes}
    created_activities = []
    for strava_activity in new_activities:
        shoes = strava_activity.shoes
        distance = strava_activity.distance
        shoe_distance = shoe_distance_mapping[shoes]
        created_activities.append(Activity(
            user=request.user,
            strava_id=strava_activity.id,
            type=STRAVA_SPORT_TYPES.get(strava_activity.type),
            shoes=shoes,
            distance=distance,
            duration=strava_activity.moving_time,
            created=strava_activity.created,
            shoe_distance=shoe_distance,
        ))

        shoe_distance_mapping[shoes] += distance

    Activity.objects.bulk_create(created_activities)
    messages.success(request, f'{len(created_activities)} new activities have been added')
    return redirect('web:activities:index')


@require_POST
@login_required
def mark_no_photos(request: TrackerHttpRequest, id: int) -> HttpResponse:
    activity = get_object_or_404(request.user.activities, id=id)
    activity.no_photos = not (activity.no_photos)
    activity.save(update_fields=['no_photos'])
    messages.success(request, 'Activity has been updated')
    return redirect('web:activities:details', activity.id)
