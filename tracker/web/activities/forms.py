from typing import Any, Optional

from django import forms
from django.db.models import TextChoices, QuerySet

from libraries.strava import STRAVA_SPORT_TYPES
from tracker.apps.activities.models import Activity
from tracker.apps.photos.models import Photo
from tracker.apps.shoes.models import Shoes
from tracker.apps.users.models import User


class ActivityFilterForm(forms.Form):
    class Filter(TextChoices):
        ALL = 'all'
        NEW = 'new'

    filter = forms.ChoiceField(required=False, initial=Filter.NEW, choices=Filter.choices)
    page = forms.IntegerField(required=False)

    def clean_page(self) -> int:
        page = self.cleaned_data['page'] or 1
        if page <= 0:
            page = 1
        return page

    def filter_activities(self, activity_qs: QuerySet) -> QuerySet:
        filter = self.cleaned_data['filter']

        if filter != self.Filter.ALL:
            activity_qs = activity_qs.filter(photos=None).exclude(no_photos=True)

        return activity_qs

    def get_selected_tab(self) -> str:
        filter = self.cleaned_data.get('filter')
        return 'index_all' if filter == self.Filter.ALL else 'index'


class AddActivityForm(forms.Form):
    id = forms.CharField()
    name = forms.CharField()
    distance = forms.FloatField()
    duration = forms.IntegerField()
    type = forms.CharField()
    shoes_id = forms.CharField()
    created = forms.DateTimeField()

    def __init__(self, user: User, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_id(self) -> str:
        id = self.cleaned_data['id']
        if self.user.activities.filter(strava_id=id).exists():
            raise forms.ValidationError('Duplicate activity ID', 'duplicate_id')
        return id

    def clean_type(self) -> Activity.Type:
        type = self.cleaned_data['type']
        activity_type = STRAVA_SPORT_TYPES.get(type)
        if not activity_type:
            raise forms.ValidationError('Invalid type', 'invalid_type')
        return activity_type

    def clean_shoes_id(self) -> Shoes:
        strava_id = self.cleaned_data['shoes_id']
        shoes = self.user.shoes.filter(strava_id=strava_id).first()
        if not shoes:
            raise forms.ValidationError('Invalid shoes ID', 'invalid_shoes_id')
        return shoes

    def save(self) -> Activity:
        shoes = self.cleaned_data['shoes_id']
        created = self.cleaned_data['created']
        distance = self.cleaned_data['distance']
        latest_activity = shoes.activities.order_by('-created').filter(created__lt=created).first()
        if latest_activity:
            current_distance_traveled = latest_activity.shoe_distance + distance
        else:
            current_distance_traveled = 0

        activity = self.user.activities.create(
            strava_id=self.cleaned_data['id'],
            name=self.cleaned_data['name'],
            type=self.cleaned_data['type'],
            shoes=shoes,
            distance=distance,
            duration=self.cleaned_data['duration'],
            created=created,
            shoe_distance=current_distance_traveled,
        )
        return activity


class ActivityPhotoForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ['category', 'file']

    def __init__(self, shoes: Shoes, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = shoes.photo_categories.all()
        self.fields['file'].required = False

    def save(self) -> Optional[Photo]:
        if not self.cleaned_data['file']:
            return None
        return super().save()


class BaseActivityPhotoFormSet(forms.BaseFormSet):
    def __init__(self, activity: Activity, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.activity = activity

    def clean(self) -> None:
        if any(self.errors):
            return
        for form in self.forms:
            form.instance.activity = self.activity
