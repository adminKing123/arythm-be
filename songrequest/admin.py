from django.contrib import admin
from .models import SongRequest

@admin.register(SongRequest)
class SongRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "name", "status")  # Columns displayed in the list view
    list_filter = ("status",)  # Sidebar filters
    search_fields = ("name", "user__username")  # Searchable fields
    ordering = ("-id",)  # Default sorting (latest first)
