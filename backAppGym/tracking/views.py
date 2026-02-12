from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from datetime import date, datetime, timedelta
from .models import WorkoutLog, SetLog
from .serializers import WorkoutLogSerializer, SetLogSerializer


class WorkoutLogViewSet(viewsets.ModelViewSet):
    """
    CRUD para logs de entrenamientos
    
    ✅ ACTUALIZADO: Ahora usa day_order para diferenciar días duplicados
    """
    serializer_class = WorkoutLogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['date', 'completed']
    ordering_fields = ['date', 'day_order']
    ordering = ['-date', 'day_order']
    
    def get_queryset(self):
        return WorkoutLog.objects.filter(
            user=self.request.user,
            is_active=True
        ).select_related('workout_day', 'user')
    
    def perform_create(self, serializer):
        """
        ✅ CRÍTICO: Asignar el usuario autenticado al crear el log
        """
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def toggle_completion(self, request):
        """
        Toggle completado de un día de entrenamiento
        
        ✅ ACTUALIZADO: Ahora requiere day_order para evitar duplicados
        
        Request body:
        {
            "workout_day_id": 5,
            "day_order": 3,  ← REQUERIDO: posición en la semana
            "date": "2026-02-11",  ← OPCIONAL: default hoy
            "week_assignment_id": 2  ← OPCIONAL
        }
        
        Response:
        {
            "id": 123,
            "workout_day": 5,
            "workout_day_name": "Tren Superior",
            "day_order": 3,
            "date": "2026-02-11",
            "completed": true,
            ...
        }
        """
        user = request.user
        workout_day_id = request.data.get('workout_day_id')
        day_order = request.data.get('day_order')
        week_assignment_id = request.data.get('week_assignment_id')
        log_date = request.data.get('date', str(date.today()))
        
        # Validaciones
        if not workout_day_id:
            return Response(
                {'error': 'workout_day_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if day_order is None:
            return Response(
                {'error': 'day_order is required to differentiate duplicate workout days'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Convertir day_order a int
            day_order = int(day_order)
            
            # ✅ Buscar por workout_day_id, day_order Y fecha
            log, created = WorkoutLog.objects.get_or_create(
                user=user,
                workout_day_id=workout_day_id,
                day_order=day_order,  # ✅ CLAVE: incluir posición
                date=log_date,
                defaults={
                    'completed': True,
                    'is_active': True,
                    'week_assignment_id': week_assignment_id
                }
            )
            
            if not created:
                # Si ya existe, toggle el estado
                log.completed = not log.completed
                log.is_active = log.completed
                log.save()
            
            serializer = WorkoutLogSerializer(log)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except ValueError:
            return Response(
                {'error': 'day_order must be an integer'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def my_logs(self, request):
        """
        Obtener logs del usuario para una fecha específica
        
        Query params:
        - date: fecha (YYYY-MM-DD), default: hoy
        - completed: true/false, filter by completion status
        
        Response: Lista de logs completados
        """
        log_date = request.query_params.get('date', str(date.today()))
        completed_filter = request.query_params.get('completed', 'true')
        
        completed_bool = completed_filter.lower() == 'true'
        
        logs = WorkoutLog.objects.filter(
            user=request.user,
            date=log_date,
            is_active=True,
            completed=completed_bool
        ).select_related('workout_day')
        
        serializer = WorkoutLogSerializer(logs, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def weekly_summary(self, request):
        """
        Resumen de la semana actual
        
        Query params:
        - week_start: fecha de inicio (YYYY-MM-DD), default: lunes de esta semana
        
        Response:
        {
            "week_start": "2026-02-10",
            "week_end": "2026-02-16",
            "total_workouts": 5,
            "completed_workouts": 3,
            "completion_rate": 60.0
        }
        """
        # Calcular inicio de semana (lunes)
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        
        # Permitir override
        week_start_str = request.query_params.get('week_start')
        if week_start_str:
            week_start = datetime.strptime(week_start_str, '%Y-%m-%d').date()
            week_end = week_start + timedelta(days=6)
        
        logs = WorkoutLog.objects.filter(
            user=request.user,
            date__gte=week_start,
            date__lte=week_end,
            is_active=True
        )
        
        total = logs.count()
        completed = logs.filter(completed=True).count()
        rate = (completed / total * 100) if total > 0 else 0
        
        return Response({
            'week_start': str(week_start),
            'week_end': str(week_end),
            'total_workouts': total,
            'completed_workouts': completed,
            'completion_rate': round(rate, 1)
        })


class SetLogViewSet(viewsets.ModelViewSet):
    """CRUD para logs de series individuales"""
    serializer_class = SetLogSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return SetLog.objects.filter(
            workout_log__user=self.request.user,
            is_active=True
        ).select_related('workout_log', 'exercise')