from django.contrib import admin

from core.accounts.models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("username", "name")
    search_fields = ["username", "name"]
