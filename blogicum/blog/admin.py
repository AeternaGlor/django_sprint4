from django.contrib import admin
from .models import Post, Category, Location


@admin.register(Post)
class PostModelAdmin(admin.ModelAdmin):
    pass


@admin.register(Category)
class CategoryModelAdmin(admin.ModelAdmin):
    pass


@admin.register(Location)
class LocationModelAdmin(admin.ModelAdmin):
    pass
