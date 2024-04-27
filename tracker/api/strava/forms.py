from django import forms

from httpx import HTTPStatusError

from libraries.strava import authorize_user
from tracker.apps.users.models import User


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
        return self.profile.user
