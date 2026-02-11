from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from core.models import BaseModel
from users.models import User
from workouts.models import (
    WorkoutWeekTemplate, 
    WorkoutDayTemplate, 
    WorkoutDayExercise
)


class UserWeekAssignment(BaseModel):
    """Assigns a workout week template to a user"""
    user = models.ForeignKey(  # CAMBIADO: OneToOneField → ForeignKey
        User,
        on_delete=models.CASCADE,
        related_name='week_assignments'  # CAMBIADO: plural
    )
    week_template = models.ForeignKey(
        WorkoutWeekTemplate,
        on_delete=models.PROTECT,
        related_name='user_assignments'
    )
    start_date = models.DateField()
    
    class Meta:
        db_table = 'user_week_assignments'
        # AGREGADO: Constraint para evitar duplicados de semana activa
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'week_template', 'start_date'],
                name='unique_user_week_start'
            ),
        ]
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['user', 'start_date']),  # NUEVO: Para queries por fecha
        ]
        ordering = ['-start_date']  # NUEVO: Más recientes primero
    
    def __str__(self):
        status = "Active" if self.is_active else "Inactive"
        return f"{self.user.email} - {self.week_template.name} ({status})"


class UserCustomWorkoutDay(BaseModel):
    """Custom workout day order/configuration for specific user"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='custom_workout_days'
    )
    workout_day = models.ForeignKey(
        WorkoutDayTemplate,
        on_delete=models.PROTECT,
        related_name='user_customizations'
    )
    day_order = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(7)]
    )
    
    class Meta:
        db_table = 'user_custom_workout_days'
        ordering = ['user', 'day_order']
        unique_together = [['user', 'day_order']]
        indexes = [
            models.Index(fields=['user', 'day_order']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - Day {self.day_order}: {self.workout_day}"


class UserCustomExerciseConfig(BaseModel):
    """Custom sets configuration for user-specific exercises"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='custom_exercise_configs'
    )
    workout_day_exercise = models.ForeignKey(
        WorkoutDayExercise,
        on_delete=models.CASCADE,
        related_name='user_customizations'
    )
    number_of_sets = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    
    class Meta:
        db_table = 'user_custom_exercise_configs'
        unique_together = [['user', 'workout_day_exercise']]
        indexes = [
            models.Index(fields=['user', 'workout_day_exercise']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.workout_day_exercise} ({self.number_of_sets} sets)"