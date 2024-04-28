from typing import Any

from django import forms

from tracker.apps.users.models import User
from tracker.apps.shoes.models import Shoes


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
