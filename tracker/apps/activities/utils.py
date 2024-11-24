from datetime import timedelta

from django.utils import timezone

from libraries.strava import get_athlete_activities, StravaActivity
from tracker.apps.shoes.models import Shoes
from tracker.apps.users.models import User

from .models import Activity


def update_activity_shoe_distances(shoes: Shoes) -> None:
    """ Update each activity totale shoe distance covered
    Assumes all activities are recorded
    """
    current_distance = 0
    activities = shoes.activities.order_by('created')
    for activity in activities:
        current_distance += activity.distance
        activity.shoe_distance = current_distance

    Activity.objects.bulk_update(activities, fields=['shoe_distance'])


def get_unregistered_strava_activities(user: User, days: int = 21) -> list[StravaActivity]:
    after = timezone.localtime() - timedelta(days=days)
    registered_activity_ids = set(
        user.activities.filter(created__gte=after).values_list('strava_id', flat=True)
    )
    active_shoes_mapping = {shoe.strava_id: shoe for shoe in user.shoes.filter(retired_at=None)}
    strava_activities = get_athlete_activities(user, after=after)

    new_activities = []
    for activity in strava_activities:
        shoes = active_shoes_mapping.get(activity.shoes_id)
        if str(activity.id) not in registered_activity_ids and shoes:
            activity.shoes = shoes
            new_activities.append(activity)

    return new_activities
