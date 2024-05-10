from typing import Any, Optional

from django import forms

from libraries.strava import STRAVA_SPORT_TYPES
from tracker.apps.activities.models import Activity
from tracker.apps.photos.models import Photo
from tracker.apps.shoes.models import Shoes
from tracker.apps.users.models import User


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
        activity = self.user.activities.create(
            strava_id=self.cleaned_data['id'],
            name=self.cleaned_data['name'],
            type=self.cleaned_data['type'],
            shoes=self.cleaned_data['shoes_id'],
            distance=self.cleaned_data['distance'],
            duration=self.cleaned_data['duration'],
            created=self.cleaned_data['created'],
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
