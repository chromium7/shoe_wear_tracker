from django.contrib import admin

from .models import ShoeBrand, Shoes


@admin.register(ShoeBrand)
class ShoeBrandAdmin(admin.ModelAdmin):
    pass


@admin.register(Shoes)
class ShoesAdmin(admin.ModelAdmin):
    pass
