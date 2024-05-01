from django import forms
from django.db.models import TextChoices

from httpx import HTTPStatusError

from libraries.strava import authorize_user
from tracker.apps.activities.models import Activity
from tracker.apps.users.models import User


class NotificationForm(forms.Form):
    class AspectType(TextChoices):
        CREATE = "create"
        UPDATE = "update"
        DELETE = "delete"

    class ObjectType(TextChoices):
        ACTIVITY = "activity"
        ATHLETE = "athlete"

    aspect_type = forms.ChoiceField(choices=AspectType.choices)
    object_type = forms.ChoiceField(choices=ObjectType.choices)
    object_id = forms.IntegerField()
    event_time = forms.IntegerField()
    owner_id = forms.IntegerField(required=False)
    subscription_id = forms.IntegerField()
    updates = forms.JSONField()

    def clean(self) -> dict:
        cleaned_data = super().clean()
        if self.errors:
            return cleaned_data

        aspect_type = cleaned_data["aspect_type"]
        object_type = cleaned_data["object_type"]
        object_id = cleaned_data["object_id"]
        if aspect_type in [self.AspectType.UPDATE, self.AspectType.DELETE]:
            if object_type == self.ObjectType.ATHLETE:
                self.athlete = (
                    User.objects.select_related("strava_profile")
                    .filter(strava_profile__athlete_id=object_id)
                    .first()
                )
                if not self.athlete:
                    error = forms.ValidationError('Invalid athlete ID', code='athlete_id')
                    self.add_error('object_id', error)
            else:
                self.activity = Activity.objects.filter(strava_id=object_id)
                if not self.activity:
                    error = forms.ValidationError('Invalid athlete ID', code='athlete_id')
                    self.add_error('object_id', error)

        return cleaned_data

    def save(self) -> dict:
        pass


class AuthorizationForm(forms.Form):
    code = forms.CharField(required=False)
    state = forms.IntegerField(required=False)
    error = forms.CharField(required=False)

    def clean_error(self) -> str:
        error = self.cleaned_data["error"]
        if error:
            raise forms.ValidationError("Invalid request", "error")
        return error

    def clean_state(self) -> User:
        user_id = self.cleaned_data["state"]
        user = User.objects.filter(id=user_id).select_related("strava_profile").first()
        if not user:
            raise forms.ValidationError("Invalid state", "invalid_state")

        profile = getattr(user, "strava_profile", None)
        if profile and profile.athlete_id:
            raise forms.ValidationError("Invalid state", "invalid_state")

        return user

    def clean(self) -> dict:
        cleaned_data = super().clean()
        if self.errors:
            return cleaned_data

        user = cleaned_data["state"]
        code = self.cleaned_data["code"]
        try:
            self.profile = authorize_user(user, code, commit=False)
        except HTTPStatusError:
            raise forms.ValidationError("Invalid code", "invalid_code")

        return cleaned_data

    def save(self) -> User:
        self.profile.save()
        self.profile.user.save(update_fields=["measurement_unit"])
        return self.profile.user
