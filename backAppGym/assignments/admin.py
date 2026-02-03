from django.contrib import admin
from .models import UserWeekAssignment, UserCustomWorkoutDay, UserCustomExerciseConfig


@admin.register(UserWeekAssignment)
class UserWeekAssignmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'week_template', 'start_date', 'is_active', 'created_at']
    list_filter = ['is_active', 'start_date', 'created_at']
    search_fields = ['user__email', 'week_template__name']
    ordering = ['-created_at']
    raw_id_fields = ['user', 'week_template']


@admin.register(UserCustomWorkoutDay)
class UserCustomWorkoutDayAdmin(admin.ModelAdmin):
    list_display = ['user', 'workout_day', 'day_order', 'is_active']
    list_filter = ['is_active', 'day_order']
    search_fields = ['user__email', 'workout_day__name']
    ordering = ['user', 'day_order']
    raw_id_fields = ['user', 'workout_day']


@admin.register(UserCustomExerciseConfig)
class UserCustomExerciseConfigAdmin(admin.ModelAdmin):
    list_display = ['user', 'workout_day_exercise', 'number_of_sets', 'is_active']
    list_filter = ['is_active', 'number_of_sets']
    search_fields = ['user__email']
    ordering = ['user']
    raw_id_fields = ['user', 'workout_day_exercise']