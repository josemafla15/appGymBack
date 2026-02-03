from django.db import models
from core.models import BaseModel


class MuscleGroup(models.TextChoices):
    """Muscle groups for exercise categorization"""
    # Legs
    QUADRICEPS = 'QUADRICEPS', 'Quadriceps'
    HAMSTRINGS = 'HAMSTRINGS', 'Hamstrings'
    GLUTES = 'GLUTES', 'Glutes'
    CALVES = 'CALVES', 'Calves'
    
    # Back
    LATS = 'LATS', 'Lats'
    TRAPS = 'TRAPS', 'Traps'
    LOWER_BACK = 'LOWER_BACK', 'Lower Back'
    
    # Chest
    CHEST = 'CHEST', 'Chest'
    
    # Shoulders
    FRONT_DELTS = 'FRONT_DELTS', 'Front Deltoids'
    SIDE_DELTS = 'SIDE_DELTS', 'Side Deltoids'
    REAR_DELTS = 'REAR_DELTS', 'Rear Deltoids'
    
    # Arms
    BICEPS = 'BICEPS', 'Biceps'
    TRICEPS = 'TRICEPS', 'Triceps'
    FOREARMS = 'FOREARMS', 'Forearms'
    
    # Core
    ABS = 'ABS', 'Abs'
    OBLIQUES = 'OBLIQUES', 'Obliques'


class Exercise(BaseModel):
    """Exercise definition"""
    name = models.CharField(max_length=200, unique=True)
    muscle_group = models.CharField(
        max_length=20,
        choices=MuscleGroup.choices,
        db_index=True
    )
    image_url = models.URLField(max_length=500, blank=True)
    description = models.TextField(blank=True)
    
    class Meta:
        db_table = 'exercises'
        ordering = ['name']
        indexes = [
            models.Index(fields=['muscle_group', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_muscle_group_display()})"