from django.contrib import admin
from .models import Exercise


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ['name', 'muscle_group', 'is_active', 'created_at']
    list_filter = ['muscle_group', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['name']
    list_per_page = 25