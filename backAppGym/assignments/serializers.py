from rest_framework import serializers
from .models import UserWeekAssignment, UserCustomWorkoutDay, UserCustomExerciseConfig
from workouts.models import WorkoutWeekTemplate, WorkoutDayTemplate, Exercise
from workouts.serializers import WorkoutWeekTemplateSerializer


class UserWeekAssignmentSerializer(serializers.ModelSerializer):
    """Serializer completo para leer asignaciones"""
    week_template = WorkoutWeekTemplateSerializer(read_only=True)
    
    class Meta:
        model = UserWeekAssignment
        fields = [
            'id',
            'user',
            'week_template',
            'start_date',
            'is_active',
            'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']


class UserWeekAssignmentCreateSerializer(serializers.Serializer):
    """Serializer para crear/actualizar asignaciones - acepta week_template_id"""
    week_template_id = serializers.IntegerField(required=True)
    start_date = serializers.DateField(required=True)
    
    def validate_week_template_id(self, value):
        """Validar que el template existe"""
        try:
            WorkoutWeekTemplate.objects.get(id=value, is_active=True)
        except WorkoutWeekTemplate.DoesNotExist:
            raise serializers.ValidationError("Workout week template does not exist or is not active")
        return value
    
    def create(self, validated_data):
        """Crear nueva asignación"""
        user = self.context.get('user')
        week_template_id = validated_data['week_template_id']
        start_date = validated_data['start_date']
        
        # Desactivar asignaciones anteriores
        UserWeekAssignment.objects.filter(user=user).update(is_active=False)
        
        # Crear nueva asignación
        assignment = UserWeekAssignment.objects.create(
            user=user,
            week_template_id=week_template_id,
            start_date=start_date,
            is_active=True
        )
        
        return assignment


class UserCustomWorkoutDaySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserCustomWorkoutDay
        fields = '__all__'
        read_only_fields = ['user', 'created_at']


class UserCustomExerciseConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserCustomExerciseConfig
        fields = '__all__'
        read_only_fields = ['user', 'created_at']