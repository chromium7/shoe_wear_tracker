from typing import TYPE_CHECKING

from django.db import models
from django.utils import timezone

from tracker.core.constants import MeasurementUnit
from tracker.core.model_fields import ChoicesPositiveSmallIntegerField

if TYPE_CHECKING:
    from tracker.apps.users.models import User


class Activity(models.Model):
    class Type(models.IntegerChoices):
        WALK = 1
        RUN = 2
        TRAIL = 3
        HIKE = 4

    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="activities")
    type = ChoicesPositiveSmallIntegerField(choices=Type.choices)
    shoes = models.ForeignKey("shoes.Shoes", on_delete=models.CASCADE, related_name="activities")
    name = models.CharField(blank=True)
    distance = models.FloatField(default=0, help_text="in meters")
    duration = models.IntegerField(blank=True, null=True, help_text="in seconds")
    strava_id = models.CharField(blank=True)
    created = models.DateTimeField(default=timezone.now)

    def __str__(self) -> str:
        return self.name or f"Activity #{self.id}"

    @classmethod
    def update_or_create_from_strava(self, strava_id: str, user: "User") -> "Activity":
        """Creates activity from strava ID
        Duplicate activity should be validated outside this function.
        """
        from libraries.strava import get_activity, STRAVA_SPORT_TYPES, StravaException

        response = get_activity(strava_id, user)
        response.raise_for_status()
        data = response.json()

        sport_type = STRAVA_SPORT_TYPES.get(data["sport_type"])
        if not sport_type:
            raise StravaException("Invalid strava sport type")

        gear_id = data.get("gear_id")
        shoes = user.shoes.filter(strava_id=gear_id).first()
        if not shoes:
            raise StravaException("Invalid activity gear ID")

        updated_data = {
            'type': sport_type,
            'shoes': shoes,
            'name': data['name'],
            'duration': data['moving_time'],  # in seconds
            'distance': data['distance'],  # in meters
        }
        activity, _ = Activity.objects.update_or_create(
            user=user,
            strava_id=data["id"],
            defaults=updated_data,
        )
        return activity

    @property
    def average_speed(self) -> str:
        if not self.distance or not self.duration:
            return '-'
        unit = self.user.measurement_unit
        if unit == MeasurementUnit.METRIC:
            distance = self.distance / 1000.0
            unit_display = 'km/h'
        else:
            distance = self.distance / 1609.344
            unit_display = 'mph'

        avg_speed = distance / (self.duration / 3600.0)
        return f'{avg_speed:.2f} {unit_display}'

    @property
    def average_pace(self) -> str:
        if not self.distance or not self.duration:
            return '-'
        unit = self.user.measurement_unit
        if unit == MeasurementUnit.METRIC:
            distance = self.distance / 1000.0
            unit_display = 'min/km'
        else:
            distance = self.distance / 1609.344
            unit_display = 'min/mile'

        avg_pace_seconds = self.duration / distance
        avg_pace_minutes = avg_pace_seconds / 60.0
        return f'{avg_pace_minutes:.2f} {unit_display}'

    def get_distance_display(self) -> str:
        if not self.distance:
            return '-'
        unit = self.user.measurement_unit
        if unit == MeasurementUnit.METRIC:
            distance = self.distance / 1000.0
        else:
            distance = self.distance / 1609.344
        return f'{distance:.2f} {self.user.get_distance_unit}(s)'
