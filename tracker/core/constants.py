from django.db.models import IntegerChoices

class MeasurementUnit(IntegerChoices):
    METRIC = 1
    MILES = 2
