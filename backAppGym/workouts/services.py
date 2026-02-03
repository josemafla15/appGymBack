from django.db import transaction
from django.core.exceptions import ValidationError
from .models import WorkoutDayTemplate, WorkoutDayExercise
from exercises.models import Exercise


class WorkoutDayService:
    """Business logic for workout days"""
    
    @staticmethod
    @transaction.atomic
    def add_exercise_to_day(workout_day_id, exercise_id, order, number_of_sets):
        """Add exercise to workout day with validation"""
        try:
            workout_day = WorkoutDayTemplate.objects.get(id=workout_day_id, is_active=True)
            exercise = Exercise.objects.get(id=exercise_id, is_active=True)
        except (WorkoutDayTemplate.DoesNotExist, Exercise.DoesNotExist):
            raise ValidationError("Workout day or exercise not found")
        
        # Validate muscle group compatibility
        allowed_groups = WorkoutDayTemplate.get_allowed_muscle_groups(
            workout_day.type
        )
        
        if exercise.muscle_group not in allowed_groups:
            raise ValidationError(
                f"Exercise '{exercise.name}' is not compatible with "
                f"{workout_day.get_type_display()}"
            )
        
        # Create the assignment
        workout_day_exercise = WorkoutDayExercise.objects.create(
            workout_day=workout_day,
            exercise=exercise,
            order=order,
            number_of_sets=number_of_sets
        )
        
        return workout_day_exercise
    
    @staticmethod
    def get_exercises_for_day(workout_day_id):
        """Get ordered exercises for a workout day"""
        return WorkoutDayExercise.objects.filter(
            workout_day_id=workout_day_id,
            is_active=True
        ).select_related('exercise').order_by('order')