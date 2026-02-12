from django.db import models
from users.models import User
from workouts.models import WorkoutDayTemplate
from assignments.models import UserWeekAssignment


class SetLog(models.Model):
    """Registro de una serie individual dentro de un workout log"""
    
    workout_log = models.ForeignKey(
        'WorkoutLog',
        on_delete=models.CASCADE,
        related_name='set_logs'
    )
    
    exercise = models.ForeignKey(
        'exercises.Exercise',
        on_delete=models.CASCADE
    )
    
    set_number = models.IntegerField()
    reps = models.IntegerField()
    weight = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'set_logs'
        ordering = ['set_number']
    
    def __str__(self):
        return f"Set {self.set_number}: {self.exercise.name} - {self.reps} reps @ {self.weight}kg"


class WorkoutLog(models.Model):
    """
    Registro de entrenamientos completados por usuario
    
    ✅ ACTUALIZADO: Ahora incluye day_order para diferenciar días 
    con el mismo template en diferentes posiciones de la semana
    """
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='workout_logs'
    )
    
    workout_day = models.ForeignKey(
        WorkoutDayTemplate,
        on_delete=models.CASCADE,
        related_name='logs'
    )
    
    # ✅ NUEVO: Posición del día en la semana
    day_order = models.IntegerField(
        default=1,
        help_text="Posición del día en la semana (1, 2, 3, etc.)"
    )
    
    # ✅ NUEVO (OPCIONAL): Referencia a la asignación de semana
    week_assignment = models.ForeignKey(
        UserWeekAssignment,
        on_delete=models.CASCADE,
        related_name='workout_logs',
        null=True,
        blank=True,
        help_text="Asignación de semana a la que pertenece este log"
    )
    
    date = models.DateField()
    completed = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'workout_logs'
        # ✅ IMPORTANTE: Unique constraint para evitar duplicados
        # Un usuario no puede tener dos logs del mismo día (workout_day + day_order) en la misma fecha
        unique_together = [
            ('user', 'workout_day', 'day_order', 'date')
        ]
        ordering = ['-date', 'day_order']
    
    def __str__(self):
        return f"{self.user.email} - Day {self.day_order}: {self.workout_day.name} - {self.date}"