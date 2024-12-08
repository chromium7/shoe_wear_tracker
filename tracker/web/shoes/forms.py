from typing import Any, Tuple

from django import forms

from tracker.apps.users.models import User
from tracker.apps.shoes.models import Shoes
from tracker.apps.photos.models import PhotoCategory, Photo


class AddShoesForm(forms.Form):
    id = forms.CharField()
    name = forms.CharField()
    distance_covered = forms.IntegerField()

    def __init__(self, user: User, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_id(self) -> str:
        id = self.cleaned_data['id']
        if self.user.shoes.filter(strava_id=id).exists():
            raise forms.ValidationError('Duplicate shoe ID', 'duplicate_id')
        return id

    def save(self) -> Shoes:
        shoes = self.user.shoes.create(
            strava_id=self.cleaned_data['id'],
            name=self.cleaned_data['name'],
            distance_covered=self.cleaned_data['distance_covered'],
        )
        return shoes


class PhotoCategoryForm(forms.ModelForm):
    class Meta:
        model = PhotoCategory
        fields = ['name']

    def __init__(self, shoes: Shoes, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.instance.shoes = shoes


class PhotoComparisonForm(forms.Form):
    shoes = forms.ModelChoiceField(queryset=None)
    photo_category = forms.IntegerField(widget=forms.HiddenInput)
    activity_1 = forms.IntegerField(widget=forms.HiddenInput)
    activity_2 = forms.IntegerField(widget=forms.HiddenInput)

    def __init__(self, user: User, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.fields['shoes'].queryset = user.shoes.all()

    def clean(self) -> dict:
        cleaned_data = super().clean()
        if self.errors:
            return cleaned_data

        shoes = cleaned_data['shoes']
        photo_category_id = cleaned_data['photo_category']
        activity_1_id = cleaned_data['activity_1']
        activity_2_id = cleaned_data['activity_2']

        photo_category = shoes.photo_categories.filter(id=photo_category_id).first()
        if not photo_category:
            error = forms.ValidationError('Invalid photo category', 'invalid_photo_category')
            self.add_error('photo_category', error)
            return cleaned_data

        activity_1 = shoes.activities.filter(id=activity_1_id).first()
        if not activity_1:
            error = forms.ValidationError('Invalid activity', 'invalid_activity')
            self.add_error('activity_1', error)

        activity_2 = shoes.activities.filter(id=activity_2_id).first()
        if not activity_2:
            error = forms.ValidationError('Invalid activity', 'invalid_activity')
            self.add_error('activity_2', error)

        if activity_1 == activity_2:
            error = forms.ValidationError('Same activities selected', 'same_activities')
            self.add_error('activity_2', error)

        cleaned_data['photo_category'] = photo_category
        return cleaned_data

    def get_photos(self) -> Tuple[Photo, Photo]:
        category = self.cleaned_data['photo_category']
        activity_1 = self.cleaned_data['activity_1']
        activity_2 = self.cleaned_data['activity_2']

        photo_1 = category.photos.filter(activity=activity_1).first()
        photo_2 = category.photos.filter(activity=activity_2).first()

        return photo_1, photo_2
