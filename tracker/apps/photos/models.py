from thumbnails.fields import ImageField

from django.db import models
from django.utils import timezone


class PhotoCategory(models.Model):
    shoes = models.ForeignKey('shoes.Shoes', on_delete=models.CASCADE, related_name='photo_categories')
    name = models.CharField()

    def __str__(self) -> str:
        return self.name


class Photo(models.Model):
    category = models.ForeignKey(PhotoCategory, on_delete=models.SET_NULL, related_name='photos', null=True)
    activity = models.ForeignKey('activities.Activity', on_delete=models.CASCADE, related_name='photos')
    file = ImageField(upload_to='photos/%Y/%m/%d')
    created = models.DateTimeField(default=timezone.now)
