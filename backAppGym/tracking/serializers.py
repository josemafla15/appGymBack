from rest_framework import serializers
from .models import WorkoutLog, SetLog


class SetLogSerializer(serializers.ModelSerializer):
    exercise_name = serializers.CharField(source='exercise.name', read_only=True)
    
    class Meta:
        model = SetLog
        fields = [
            'id',
            'workout_log',
            'exercise',
            'exercise_name',
            'set_number',
            'reps',
            'weight',
            'notes',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class WorkoutLogSerializer(serializers.ModelSerializer):
    """
    Serializer para WorkoutLog
    
    ✅ Acepta tanto workout_day como workout_day_id para compatibilidad
    """
    workout_day_name = serializers.CharField(
        source='workout_day.name',
        read_only=True
    )
    workout_day_type = serializers.CharField(
        source='workout_day.type',
        read_only=True
    )
    set_logs = SetLogSerializer(many=True, read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = WorkoutLog
        fields = [
            'id',
            'user',
            'user_email',
            'workout_day',
            'workout_day_name',
            'workout_day_type',
            'day_order',
            'week_assignment',
            'date',
            'completed',
            'notes',
            'set_logs',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def to_internal_value(self, data):
        """
        ✅ SOLUCIÓN: Convertir workout_day_id a workout_day antes de validar
        """
        # Si viene workout_day_id en lugar de workout_day, convertirlo
        if 'workout_day_id' in data and 'workout_day' not in data:
            data = data.copy()  # Hacer una copia para no mutar el original
            data['workout_day'] = data.pop('workout_day_id')
        
        return super().to_internal_value(data)


class WorkoutLogListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listas"""
    workout_day_name = serializers.CharField(source='workout_day.name', read_only=True)
    
    class Meta:
        model = WorkoutLog
        fields = [
            'id',
            'workout_day',
            'workout_day_name',
            'day_order',
            'date',
            'completed'
        ]