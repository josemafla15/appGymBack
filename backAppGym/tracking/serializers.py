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
    
    ✅ SOLUCIÓN: NO usar to_internal_value(), solo validate()
    ✅ FIX: Asegurar que completed sea False por defecto
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
    
    # ✅ Campo write-only para aceptar el ID desde el frontend
    workout_day_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = WorkoutLog
        fields = [
            'id',
            'user',
            'user_email',
            'workout_day',
            'workout_day_id',
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
        # ✅ CRÍTICO: Hacer workout_day opcional para que NO falle la validación
        extra_kwargs = {
            'workout_day': {'required': False},
            'completed': {'required': False}  # ✅ NUEVO: completed también opcional
        }
    
    def validate(self, attrs):

        # ✅ SOLO validar en creación
        if self.instance is None:
        
            workout_day_id = attrs.pop('workout_day_id', None)
    
            if workout_day_id is not None:
                from workouts.models import WorkoutDayTemplate
                try:
                    workout_day = WorkoutDayTemplate.objects.get(
                        id=workout_day_id,
                        is_active=True
                    )
                    attrs['workout_day'] = workout_day
                except WorkoutDayTemplate.DoesNotExist:
                    raise serializers.ValidationError({
                        'workout_day_id': 'Workout day template not found or inactive'
                    })
    
            if 'workout_day' not in attrs:
                raise serializers.ValidationError({
                    'workout_day': 'Either workout_day or workout_day_id is required'
                })
    
            if 'completed' not in attrs:
                attrs['completed'] = False
    
        return attrs



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