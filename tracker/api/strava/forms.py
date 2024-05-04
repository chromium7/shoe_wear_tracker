from typing import Optional

from django import forms
from django.db.models import TextChoices

from httpx import HTTPStatusError

from libraries.strava import authorize_user
from tracker.apps.activities.models import Activity
from tracker.apps.users.models import User


class NotificationForm(forms.Form):
    class AspectType(TextChoices):
        CREATE = 'create'
        UPDATE = 'update'
        DELETE = 'delete'

    class ObjectType(TextChoices):
        ACTIVITY = 'activity'
        ATHLETE = 'athlete'

    aspect_type = forms.ChoiceField(choices=AspectType.choices)
    object_type = forms.ChoiceField(choices=ObjectType.choices)
    object_id = forms.IntegerField()
    event_time = forms.IntegerField()
    owner_id = forms.IntegerField()
    subscription_id = forms.IntegerField()
    updates = forms.JSONField()

    def clean_owner_id(self) -> User:
        owner_id = self.cleaned_data['owner_id']
        user = User.objects.filter(strava__profile__athlete_id=owner_id).first()
        if not user:
            raise forms.ValidationError('Invalid owner ID', 'invalid_owner_id')
        return user

    def clean(self) -> dict:
        cleaned_data = super().clean()
        if self.errors:
            return cleaned_data

        aspect_type = cleaned_data['aspect_type']
        object_type = cleaned_data['object_type']
        object_id = cleaned_data['object_id']
        user = cleaned_data['owner_id']
        updates = self.cleaned_data['updates']
        # We don't care about profile updates
        if object_type == self.ObjectType.ATHLETE:
            error = forms.ValidationError('Invalid object type', 'invalid_object_type')
            self.add_error('object_type', error)
            return cleaned_data

        self.activity = Activity.objects.filter(strava_id=object_id).first()
        if aspect_type == self.AspectType.DELETE and not self.activity:
            error = forms.ValidationError(f'Activity ID {object_id} not found', 'invalid_activity_id')
            self.add_error('object_id', error)
            return cleaned_data

        if self.aspect_type != self.AspectType.DELETE:
            gear_id = updates.get('gear_id')
            self.shoes = user.shoes.filter(strava_id=gear_id).first()
            if not self.shoes:
                error = forms.ValidationError(f'Invalid gear ID {gear_id}', 'invalid_gear_id')
                self.add_error('updates', error)

        return cleaned_data

    def save(self) -> Optional[Activity]:
        user = self.cleaned_data['owner_id']
        aspect_type = self.cleaned_data['aspect_type']
        object_id = self.cleaned_data['object_id']
        activity: Optional[Activity] = None
        if aspect_type == self.AspectType.DELETE:
            self.activity.delete()
            activity = None
        else:
            # Correct shoe is used
            activity = Activity.update_or_create_from_strava(object_id, user)

        return activity


class AuthorizationForm(forms.Form):
    code = forms.CharField(required=False)
    state = forms.IntegerField(required=False)
    error = forms.CharField(required=False)

    def clean_error(self) -> str:
        error = self.cleaned_data['error']
        if error:
            raise forms.ValidationError('Invalid request', 'error')
        return error

    def clean_state(self) -> User:
        user_id = self.cleaned_data['state']
        user = User.objects.filter(id=user_id).select_related('strava_profile').first()
        if not user:
            raise forms.ValidationError('Invalid state', 'invalid_state')

        profile = getattr(user, 'strava_profile', None)
        if profile and profile.athlete_id:
            raise forms.ValidationError('Invalid state', 'invalid_state')

        return user

    def clean(self) -> dict:
        cleaned_data = super().clean()
        if self.errors:
            return cleaned_data

        user = cleaned_data['state']
        code = self.cleaned_data['code']
        try:
            self.profile = authorize_user(user, code, commit=False)
        except HTTPStatusError:
            raise forms.ValidationError('Invalid code', 'invalid_code')

        return cleaned_data

    def save(self) -> User:
        self.profile.save()
        self.profile.user.save(update_fields=['measurement_unit'])
        return self.profile.user
