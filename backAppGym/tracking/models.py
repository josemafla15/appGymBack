from django.db import models
from django.core.validators import MinValueValidator
from core.models import BaseModel
from users.models import User
from workouts.models import WorkoutDayTemplate
from exercises.models import Exercise


class WorkoutLog(BaseModel):
    """Log of a completed workout day"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='workout_logs'
    )
    workout_day = models.ForeignKey(
        WorkoutDayTemplate,
        on_delete=models.PROTECT,
        related_name='logs'
    )
    date = models.DateField(db_index=True)
    completed = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'workout_logs'
        ordering = ['-date', '-created_at']
        unique_together = [['user', 'workout_day', 'date']]
        indexes = [
            models.Index(fields=['user', 'date']),
            models.Index(fields=['user', 'completed']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.workout_day} - {self.date}"


class SetLog(BaseModel):
    """Log of individual sets performed"""
    workout_log = models.ForeignKey(
        WorkoutLog,
        on_delete=models.CASCADE,
        related_name='set_logs'
    )
    exercise = models.ForeignKey(
        Exercise,
        on_delete=models.PROTECT,
        related_name='set_logs'
    )
    set_number = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )
    reps = models.PositiveIntegerField(
        validators=[MinValueValidator(0)]
    )
    weight = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )
    
    class Meta:
        db_table = 'set_logs'
        ordering = ['workout_log', 'exercise', 'set_number']
        unique_together = [['workout_log', 'exercise', 'set_number']]
        indexes = [
            models.Index(fields=['workout_log', 'exercise']),
        ]
    
    def __str__(self):
        return (
            f"{self.workout_log.user.email} - {self.exercise.name} - "
            f"Set {self.set_number}: {self.reps} reps"
        )