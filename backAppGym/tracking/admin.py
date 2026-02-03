from django.contrib import admin
from .models import WorkoutLog, SetLog


class SetLogInline(admin.TabularInline):
    model = SetLog
    extra = 0
    fields = ['exercise', 'set_number', 'reps', 'weight', 'is_active']
    raw_id_fields = ['exercise']


@admin.register(WorkoutLog)
class WorkoutLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'workout_day', 'date', 'completed', 'is_active', 'created_at']
    list_filter = ['completed', 'is_active', 'date', 'created_at']
    search_fields = ['user__email', 'workout_day__name']
    ordering = ['-date', '-created_at']
    raw_id_fields = ['user', 'workout_day']
    inlines = [SetLogInline]


@admin.register(SetLog)
class SetLogAdmin(admin.ModelAdmin):
    list_display = ['workout_log', 'exercise', 'set_number', 'reps', 'weight', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['workout_log__user__email', 'exercise__name']
    ordering = ['-created_at']
    raw_id_fields = ['workout_log', 'exercise']