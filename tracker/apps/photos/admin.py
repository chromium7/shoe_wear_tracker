from django.contrib import admin

from .models import PhotoCategory, Photo


@admin.register(PhotoCategory)
class PhotoCategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    pass
