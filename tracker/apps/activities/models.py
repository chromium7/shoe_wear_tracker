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
    shoe_distance = models.FloatField(blank=True, null=True, help_text="in meters")
    strava_id = models.CharField(blank=True)
    created = models.DateTimeField(default=timezone.now)

    def __str__(self) -> str:
        return self.name or f"Activity #{self.id}"

    @classmethod
    def update_or_create_from_strava(self, strava_id: str, user: "User") -> "Activity":
        """Creates activity from strava ID
        Duplicate activity should be validated outside this function.
        """
        from libraries.strava import get_athlete_activity, StravaException

        strava_activity = get_athlete_activity(strava_id, user)
        if not strava_activity:
            raise StravaException("Invalid activity ID")

        shoes = user.shoes.filter(strava_id=strava_activity.shoes_id).first()
        if not shoes:
            raise StravaException("Invalid activity gear ID")

        latest_activity = shoes.activities.order_by('-created').filter(created__lt=strava_activity.created).first()
        current_distance_traveled = latest_activity.shoe_distance + strava_activity.distance
        updated_data = {
            'type': strava_activity.type,
            'shoes': shoes,
            'name': strava_activity.name,
            'duration': strava_activity.moving_time,  # in seconds
            'distance': strava_activity.distance,  # in meters
            'created': strava_activity.created,
            'shoe_distance': current_distance_traveled,
        }
        activity, _ = Activity.objects.update_or_create(
            user=user,
            strava_id=strava_activity.id,
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

        pace_in_minutes = self.duration / distance / 60.0
        minutes = int(pace_in_minutes)
        seconds = int((pace_in_minutes - minutes) * 60)
        return f'{minutes}:{seconds:02d} {unit_display}'

    def get_shoe_distance_display(self) -> str:
        if not self.shoe_distance:
            return '-'
        unit = self.user.measurement_unit
        if unit == MeasurementUnit.METRIC:
            shoe_distance = self.shoe_distance / 1000.0
        else:
            shoe_distance = self.shoe_distance / 1609.344
        return f'{shoe_distance:.2f} {self.user.get_distance_unit()}'

    def get_distance_display(self) -> str:
        if not self.distance:
            return '-'
        unit = self.user.measurement_unit
        if unit == MeasurementUnit.METRIC:
            distance = self.distance / 1000.0
        else:
            distance = self.distance / 1609.344
        return f'{distance:.2f} {self.user.get_distance_unit()}'

    def get_duration_display(self) -> str:
        if not self.duration:
            return '-'
        duration_in_min = self.duration // 60
        return f'{duration_in_min} minutes'
