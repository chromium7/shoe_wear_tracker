from tracker.apps.shoes.models import Shoes
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
