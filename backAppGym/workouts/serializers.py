from rest_framework import serializers
from exercises.models import Exercise
from exercises.serializers import ExerciseSerializer, ExerciseListSerializer
from .models import (
    WorkoutDayTemplate,
    WorkoutDayExercise,
    WorkoutWeekTemplate,
    WorkoutWeekDay,
)


class WorkoutDayExerciseSerializer(serializers.ModelSerializer):
    exercise = ExerciseListSerializer(read_only=True)
    exercise_id = serializers.PrimaryKeyRelatedField(
        queryset=Exercise.objects.filter(is_active=True),
        source='exercise',
        write_only=True
    )
    
    class Meta:
        model = WorkoutDayExercise
        fields = [
            'id',
            'exercise',
            'exercise_id',
            'order',
            'number_of_sets',
        ]
        read_only_fields = ['id']


class WorkoutDayTemplateSerializer(serializers.ModelSerializer):
    exercises = WorkoutDayExerciseSerializer(many=True, read_only=True)
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    
    class Meta:
        model = WorkoutDayTemplate
        fields = [
            'id',
            'type',
            'type_display',
            'name',
            'exercises',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class WorkoutDayTemplateListSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    exercise_count = serializers.SerializerMethodField()
    
    class Meta:
        model = WorkoutDayTemplate
        fields = ['id', 'type', 'type_display', 'name', 'exercise_count']
    
    def get_exercise_count(self, obj):
        return obj.exercises.filter(is_active=True).count()


class WorkoutWeekDaySerializer(serializers.ModelSerializer):
    workout_day = WorkoutDayTemplateSerializer(read_only=True)
    workout_day_id = serializers.PrimaryKeyRelatedField(
        queryset=WorkoutDayTemplate.objects.filter(is_active=True),
        source='workout_day',
        write_only=True
    )
    
    class Meta:
        model = WorkoutWeekDay
        fields = [
            'id',
            'workout_day',
            'workout_day_id',
            'day_order',
        ]
        read_only_fields = ['id']


class WorkoutWeekTemplateSerializer(serializers.ModelSerializer):
    days = WorkoutWeekDaySerializer(many=True, read_only=True)
    
    class Meta:
        model = WorkoutWeekTemplate
        fields = [
            'id',
            'name',
            'description',
            'days',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class WorkoutWeekTemplateListSerializer(serializers.ModelSerializer):
    day_count = serializers.SerializerMethodField()
    
    class Meta:
        model = WorkoutWeekTemplate
        fields = ['id', 'name', 'description', 'day_count']
    
    def get_day_count(self, obj):
        return obj.days.filter(is_active=True).count()