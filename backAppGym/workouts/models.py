from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from core.models import BaseModel
from exercises.models import Exercise, MuscleGroup


class WorkoutDayType(models.TextChoices):
    """Fixed workout day types"""
    LEG_DAY = 'LEG_DAY', 'Leg Day'
    UPPER_BODY_DAY = 'UPPER_BODY_DAY', 'Upper Body Day'
    PULL_DAY = 'PULL_DAY', 'Pull Day'
    PUSH_DAY = 'PUSH_DAY', 'Push Day'
    FULL_BODY_DAY = 'FULL_BODY_DAY', 'Full Body Day'


class WorkoutDayTemplate(BaseModel):
    """Template for a workout day structure"""
    type = models.CharField(
        max_length=20,
        choices=WorkoutDayType.choices,
        db_index=True
    )
    name = models.CharField(max_length=200, blank=True)
    
    class Meta:
        db_table = 'workout_day_templates'
        ordering = ['type']
    
    def __str__(self):
        return self.name or self.get_type_display()
    
    @classmethod
    def get_allowed_muscle_groups(cls, day_type):
        """Returns allowed muscle groups for each day type"""
        mappings = {
            WorkoutDayType.LEG_DAY: [
                MuscleGroup.QUADRICEPS,
                MuscleGroup.HAMSTRINGS,
                MuscleGroup.GLUTES,
                MuscleGroup.CALVES,
            ],
            WorkoutDayType.PULL_DAY: [
                MuscleGroup.LATS,
                MuscleGroup.TRAPS,
                MuscleGroup.LOWER_BACK,
                MuscleGroup.BICEPS,
                MuscleGroup.REAR_DELTS,
                MuscleGroup.SIDE_DELTS,
            ],
            WorkoutDayType.PUSH_DAY: [
                MuscleGroup.CHEST,
                MuscleGroup.TRICEPS,
                MuscleGroup.FRONT_DELTS,
                MuscleGroup.SIDE_DELTS,
            ],
            WorkoutDayType.UPPER_BODY_DAY: [
                MuscleGroup.LATS,
                MuscleGroup.TRAPS,
                MuscleGroup.LOWER_BACK,
                MuscleGroup.CHEST,
                MuscleGroup.FRONT_DELTS,
                MuscleGroup.SIDE_DELTS,
                MuscleGroup.REAR_DELTS,
                MuscleGroup.BICEPS,
                MuscleGroup.TRICEPS,
                MuscleGroup.FOREARMS,
                MuscleGroup.ABS,
                MuscleGroup.OBLIQUES,
            ],
            WorkoutDayType.FULL_BODY_DAY: [choice[0] for choice in MuscleGroup.choices],
        }
        return mappings.get(day_type, [])


class WorkoutDayExercise(BaseModel):
    """Exercise assignment to workout day with order and sets"""
    workout_day = models.ForeignKey(
        WorkoutDayTemplate,
        on_delete=models.CASCADE,
        related_name='exercises'
    )
    exercise = models.ForeignKey(
        Exercise,
        on_delete=models.PROTECT,
        related_name='workout_days'
    )
    order = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )
    number_of_sets = models.PositiveIntegerField(
        default=3,
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    
    class Meta:
        db_table = 'workout_day_exercises'
        ordering = ['workout_day', 'order']
        unique_together = [['workout_day', 'exercise']]
        indexes = [
            models.Index(fields=['workout_day', 'order']),
        ]
    
    def __str__(self):
        return f"{self.workout_day} - {self.exercise} (Order: {self.order})"
    
    def clean(self):
        """Validate exercise compatibility with workout day type"""
        if not self.exercise_id or not self.workout_day_id:
            return
            
        allowed_groups = WorkoutDayTemplate.get_allowed_muscle_groups(
            self.workout_day.type
        )
        
        if self.exercise.muscle_group not in allowed_groups:
            raise ValidationError(
                f"Exercise '{self.exercise.name}' with muscle group "
                f"'{self.exercise.get_muscle_group_display()}' is not allowed "
                f"in {self.workout_day.get_type_display()}"
            )
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class WorkoutWeekTemplate(BaseModel):
    """Template for a full week of workouts"""
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    
    class Meta:
        db_table = 'workout_week_templates'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class WorkoutWeekDay(BaseModel):
    """Ordered days in a workout week"""
    week_template = models.ForeignKey(
        WorkoutWeekTemplate,
        on_delete=models.CASCADE,
        related_name='days'
    )
    workout_day = models.ForeignKey(
        WorkoutDayTemplate,
        on_delete=models.PROTECT,
        related_name='week_days'
    )
    day_order = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(7)]
    )
    
    class Meta:
        db_table = 'workout_week_days'
        ordering = ['week_template', 'day_order']
        unique_together = [['week_template', 'day_order']]
        indexes = [
            models.Index(fields=['week_template', 'day_order']),
        ]
    
    def __str__(self):
        return f"{self.week_template} - Day {self.day_order}: {self.workout_day}"