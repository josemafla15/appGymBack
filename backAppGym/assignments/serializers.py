from rest_framework import serializers
from workouts.serializers import WorkoutWeekTemplateSerializer, WorkoutDayTemplateSerializer
from workouts.models import WorkoutWeekTemplate, WorkoutDayTemplate, WorkoutDayExercise
from .models import UserWeekAssignment, UserCustomWorkoutDay, UserCustomExerciseConfig


class UserWeekAssignmentSerializer(serializers.ModelSerializer):
    week_template = WorkoutWeekTemplateSerializer(read_only=True)
    week_template_id = serializers.PrimaryKeyRelatedField(
        queryset=WorkoutWeekTemplate.objects.filter(is_active=True),
        source='week_template',
        write_only=True
    )
    
    class Meta:
        model = UserWeekAssignment
        fields = [
            'id',
            'user',
            'week_template',
            'week_template_id',
            'start_date',
            'is_active',
            'created_at',
        ]
        read_only_fields = ['id', 'user', 'created_at']


class UserCustomWorkoutDaySerializer(serializers.ModelSerializer):
    workout_day = WorkoutDayTemplateSerializer(read_only=True)
    workout_day_id = serializers.PrimaryKeyRelatedField(
        queryset=WorkoutDayTemplate.objects.filter(is_active=True),
        source='workout_day',
        write_only=True
    )
    
    class Meta:
        model = UserCustomWorkoutDay
        fields = [
            'id',
            'user',
            'workout_day',
            'workout_day_id',
            'day_order',
            'is_active',
        ]
        read_only_fields = ['id', 'user']


class UserCustomExerciseConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserCustomExerciseConfig
        fields = [
            'id',
            'user',
            'workout_day_exercise',
            'number_of_sets',
            'is_active',
        ]
        read_only_fields = ['id', 'user']