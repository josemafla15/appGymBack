from django.contrib import admin
from .models import (
    WorkoutDayTemplate,
    WorkoutDayExercise,
    WorkoutWeekTemplate,
    WorkoutWeekDay,
)


class WorkoutDayExerciseInline(admin.TabularInline):
    model = WorkoutDayExercise
    extra = 1
    fields = ['exercise', 'order', 'number_of_sets', 'is_active']


@admin.register(WorkoutDayTemplate)
class WorkoutDayTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'is_active', 'created_at']
    list_filter = ['type', 'is_active', 'created_at']
    search_fields = ['name']
    ordering = ['type', 'name']
    inlines = [WorkoutDayExerciseInline]


class WorkoutWeekDayInline(admin.TabularInline):
    model = WorkoutWeekDay
    extra = 1
    fields = ['workout_day', 'day_order', 'is_active']


@admin.register(WorkoutWeekTemplate)
class WorkoutWeekTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['name']
    inlines = [WorkoutWeekDayInline]