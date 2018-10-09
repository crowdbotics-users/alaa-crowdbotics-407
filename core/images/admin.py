from django.contrib import admin
from . import models

# Register your models here.


@admin.register(models.Image)
class ImageAdmin(admin.ModelAdmin):
    search_fields = (
        'restaurant',
        'dish',
    )

    list_filter = (
        'restaurant',
        'creator'
    )

    list_display = (
        '__str__',
        'id',
        'restaurant',
        'dish',
        'creator',
        'created_at',
        'updated_at',
    )


@admin.register(models.Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = (
        'creator',
        'image',
        'created_at',
        'updated_at',
    )


@admin.register(models.Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'message',
        'creator',
        'image',
        'created_at',
        'updated_at',
    )
