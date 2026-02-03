from rest_framework import serializers
from exercises.serializers import ExerciseListSerializer
from workouts.serializers import WorkoutDayTemplateSerializer
from workouts.models import WorkoutDayTemplate
from exercises.models import Exercise
from .models import WorkoutLog, SetLog


class SetLogSerializer(serializers.ModelSerializer):
    exercise = ExerciseListSerializer(read_only=True)
    exercise_id = serializers.PrimaryKeyRelatedField(
        queryset=Exercise.objects.filter(is_active=True),
        source='exercise',
        write_only=True
    )
    
    class Meta:
        model = SetLog
        fields = [
            'id',
            'exercise',
            'exercise_id',
            'set_number',
            'reps',
            'weight',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class WorkoutLogSerializer(serializers.ModelSerializer):
    workout_day = WorkoutDayTemplateSerializer(read_only=True)
    workout_day_id = serializers.PrimaryKeyRelatedField(
        queryset=WorkoutDayTemplate.objects.filter(is_active=True),
        source='workout_day',
        write_only=True
    )
    set_logs = SetLogSerializer(many=True, read_only=True)
    
    class Meta:
        model = WorkoutLog
        fields = [
            'id',
            'user',
            'workout_day',
            'workout_day_id',
            'date',
            'completed',
            'notes',
            'set_logs',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class WorkoutLogListSerializer(serializers.ModelSerializer):
    workout_day_name = serializers.CharField(source='workout_day.name', read_only=True)
    workout_day_type = serializers.CharField(source='workout_day.get_type_display', read_only=True)
    total_sets = serializers.SerializerMethodField()
    
    class Meta:
        model = WorkoutLog
        fields = [
            'id',
            'workout_day_name',
            'workout_day_type',
            'date',
            'completed',
            'total_sets',
        ]
    
    def get_total_sets(self, obj):
        return obj.set_logs.filter(is_active=True).count()