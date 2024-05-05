from typing import Any

from django import forms

from tracker.apps.activities.models import Activity
from tracker.apps.photos.models import Photo


class ActivityPhotoForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ['category', 'file']

    def __init__(self, activity: Activity, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.instance.activity = activity
