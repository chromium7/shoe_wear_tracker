from typing import Any

from django import forms

from tracker.apps.photos.models import PhotoCategory
from tracker.apps.users.models import User


class UserShoesForm(forms.Form):
    shoes = forms.ModelChoiceField(queryset=None)

    def __init__(self, user: User, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.fields['shoes'].queryset = user.shoes.all()


class PhotoCategoriesForm(forms.Form):
    photo_category = forms.ModelChoiceField(queryset=None)

    def __init__(self, user: User, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.fields['photo_category'].queryset = PhotoCategory.objects.filter(shoes__user=user)
