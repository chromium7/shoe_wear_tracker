from django.db import models
from django.utils import timezone


class ShoeBrand(models.Model):
    name = models.CharField()

    def __str__(self) -> str:
        return self.name


class Shoes(models.Model):
    user = models.ForeignKey('users.User', related_name='shoes', on_delete=models.CASCADE)
    brand = models.ForeignKey(ShoeBrand, related_name='shoes', on_delete=models.SET_NULL, blank=True, null=True)
    name = models.CharField()
    note = models.TextField(blank=True)
    distance_covered = models.FloatField(default=0)
    created = models.DateTimeField(default=timezone.now)
    strava_id = models.CharField(blank=True)
    retired_at = models.DateTimeField(blank=True, null=True)

    def __str__(self) -> str:
        return self.name

    @property
    def retired(self) -> bool:
        return bool(self.retired_at)

    @property
    def converted_distance(self) -> float:
        return round(self.distance_covered / 1000, 1)

    def recalculate_distance_covered(self) -> None:
        self.distance_covered = (
            self.activities.aggregate(total_distance=models.Sum('distance'))['total_distance'] or 0
        )
        self.save(update_fields=['distance_covered'])

    def retire(self) -> None:
        self.retired_at = timezone.now()
        self.save(update_fields=['retired_at'])
