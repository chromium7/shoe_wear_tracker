from typing import Any

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager
from django.db import models
from django.utils import timezone

from tracker.core.constants import MeasurementUnit
from tracker.core.model_fields import ChoicesPositiveSmallIntegerField


class CustomUserManager(UserManager):

    def create_user(self, password: str, **extra_fields: Any) -> 'User':
        user = self.model(is_superuser=False, is_staff=False, is_active=True, **extra_fields)

        if password:
            user.set_password(password)

        user.save(using=self._db)
        return user

    def create_superuser(self, password: str, **extra_fields: Any) -> 'User':
        user = self.create_user(password=password, **extra_fields)
        user.is_staff = True
        user.is_active = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created = models.DateTimeField(default=timezone.now)
    measurement_unit = ChoicesPositiveSmallIntegerField(
        choices=MeasurementUnit.choices, default=MeasurementUnit.METRIC
    )

    objects = CustomUserManager()
    USERNAME_FIELD = 'username'

    def __str__(self) -> str:
        return self.username

    def get_distance_unit(self) -> str:
        if self.measurement_unit == MeasurementUnit.METRIC:
            return 'km'
        return 'miles'

    def get_pace_unit(self) -> str:
        if self.measurement_unit == MeasurementUnit.METRIC:
            return 'min/km'
        return 'min/miles'


class StravaProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='strava_profile')
    athlete_id = models.CharField()
    access_token = models.CharField()
    refresh_token = models.CharField()
    expires_at = models.IntegerField()
