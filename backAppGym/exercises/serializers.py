from rest_framework import serializers
from .models import Exercise


class ExerciseSerializer(serializers.ModelSerializer):
    muscle_group_display = serializers.CharField(source='get_muscle_group_display', read_only=True)
    
    class Meta:
        model = Exercise
        fields = [
            'id',
            'name',
            'muscle_group',
            'muscle_group_display',
            'image_url',
            'description',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ExerciseListSerializer(serializers.ModelSerializer):
    muscle_group_display = serializers.CharField(source='get_muscle_group_display', read_only=True)
    
    class Meta:
        model = Exercise
        fields = ['id', 'name', 'muscle_group', 'muscle_group_display', 'image_url']