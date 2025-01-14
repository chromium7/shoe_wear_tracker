from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse

from tracker.core.utils import TrackerHttpRequest

from .forms import UserShoesForm, PhotoCategoriesForm


@login_required
def photo_categories(request: TrackerHttpRequest) -> HttpResponse:
    form = UserShoesForm(data=request.GET or None, user=request.user)
    if form.is_valid():
        shoes = form.cleaned_data['shoes']
        photo_categories = shoes.photo_categories.all()
        data = {'categories': [{'id': category.id, 'name': category.name} for category in photo_categories]}
        return JsonResponse({'status': 'ok', 'data': data})

    return JsonResponse({'status': 'error'})


@login_required
def photos(request: TrackerHttpRequest) -> HttpResponse:
    form = PhotoCategoriesForm(data=request.GET or None, user=request.user)
    if form.is_valid():
        photo_category = form.cleaned_data['photo_category']
        photos = photo_category.photos.order_by('created').select_related('activity')

        photo_data = []
        for photo in photos:
            if photo.activity_id:
                name = f'Activity {photo.activity.get_shoe_distance_display()}'
            else:
                name = f'Photo {photo.created.strftime("%Y-%m-%d")}'

            photo_data.append({'name': name, 'url': photo.file.url})

        data = {'photos': photo_data}
        return JsonResponse({'status': 'ok', 'data': data})

    print(form.errors)
    return JsonResponse({'status': 'error'})
