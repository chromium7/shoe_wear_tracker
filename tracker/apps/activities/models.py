from django.db import models
from django.utils import timezone

from tracker.core.model_fields import ChoicesPositiveSmallIntegerField


class Activity(models.Model):
    class Type(models.IntegerChoices):
        WALK = 1
        RUN = 2
        TRAIL = 3
        HIKE = 4

    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='activities')
    type = ChoicesPositiveSmallIntegerField(choices=Type.choices)
    shoes = models.ForeignKey('shoes.Shoes', on_delete=models.CASCADE, related_name='photos')
    name = models.CharField(blank=True)
    average_pace = models.FloatField(blank=True, null=True)
    distance_covered = models.FloatField(default=0)
    strava_id = models.CharField(blank=True)
    created = models.DateTimeField(default=timezone.now)

    def __str__(self) -> str:
        return self.name or f'Activity #{self.id}'
