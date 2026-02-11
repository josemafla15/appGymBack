from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta
from core.permissions import IsAdmin
from users.models import User
from .models import UserWeekAssignment, UserCustomWorkoutDay, UserCustomExerciseConfig
from .serializers import (
    UserWeekAssignmentSerializer,
    UserWeekAssignmentCreateSerializer,
    UserCustomWorkoutDaySerializer,
    UserCustomExerciseConfigSerializer,
)


class UserAssignmentViewSet(viewsets.ViewSet):
    """
    Manage user workout assignments
    Admin can assign to any user
    Users can only view their own assignments
    """
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def my_assignment(self, request):
        """Get current user's week assignment"""
        try:
            assignment = UserWeekAssignment.objects.get(
                user=request.user,
                is_active=True
            )
            serializer = UserWeekAssignmentSerializer(assignment)
            return Response(serializer.data)
        except UserWeekAssignment.DoesNotExist:
            return Response(
                {'message': 'No workout week assigned yet'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'])
    def renew_my_week(self, request):
        """
        Usuario renueva su propia semana de entrenamiento
        Usa la misma plantilla pero con nueva fecha de inicio
        """
        try:
            # Obtener la asignación actual del usuario
            current_assignment = UserWeekAssignment.objects.get(
                user=request.user,
                is_active=True
            )
            
            # Obtener la nueva fecha de inicio (puede ser enviada o calculada)
            new_start_date = request.data.get('start_date')
            
            if not new_start_date:
                # Si no se proporciona fecha, calcular automáticamente
                # Sumar 7 días a la fecha de inicio actual
                from datetime import timedelta
                current_start = current_assignment.start_date
                new_start_date = current_start + timedelta(days=7)
            
            # Desactivar la asignación actual
            current_assignment.is_active = False
            current_assignment.save()
            
            # Crear nueva asignación con la misma plantilla
            new_assignment = UserWeekAssignment.objects.create(
                user=request.user,
                week_template=current_assignment.week_template,
                start_date=new_start_date,
                is_active=True
            )
            
            serializer = UserWeekAssignmentSerializer(new_assignment)
            return Response(
                {
                    'message': 'Week renewed successfully',
                    'assignment': serializer.data
                },
                status=status.HTTP_201_CREATED
            )
            
        except UserWeekAssignment.DoesNotExist:
            return Response(
                {'error': 'No active week assignment found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def my_week_info(self, request):
        """
        Obtener información detallada de la semana actual del usuario
        Incluye: días completados, progreso, etc.
        """
        try:
            assignment = UserWeekAssignment.objects.get(
                user=request.user,
                is_active=True
            )
            
            # Calcular información adicional
            from datetime import timedelta
            from tracking.models import WorkoutLog
            
            start_date = assignment.start_date
            end_date = start_date + timedelta(days=6)  # 7 días en total
            today = timezone.now().date()
            
            # Contar workouts completados esta semana
            completed_workouts = WorkoutLog.objects.filter(
                user=request.user,
                date__gte=start_date,
                date__lte=end_date,
                completed=True
            ).count()
            
            # Total de días en el programa
            total_days = assignment.week_template.days.count()
            
            # Días transcurridos desde el inicio
            days_elapsed = (today - start_date).days + 1
            if days_elapsed < 0:
                days_elapsed = 0
            elif days_elapsed > 7:
                days_elapsed = 7
            
            # Determinar si puede renovar (ha pasado al menos 1 semana)
            can_renew = (today - start_date).days >= 7
            
            serializer = UserWeekAssignmentSerializer(assignment)
            
            return Response({
                'assignment': serializer.data,
                'start_date': start_date,
                'end_date': end_date,
                'days_elapsed': days_elapsed,
                'total_days': total_days,
                'completed_workouts': completed_workouts,
                'completion_rate': (completed_workouts / total_days * 100) if total_days > 0 else 0,
                'can_renew': can_renew,
                'is_current_week': start_date <= today <= end_date,
            })
            
        except UserWeekAssignment.DoesNotExist:
            return Response(
                {'message': 'No workout week assigned yet'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdmin], url_path='assign-week')
    def assign_week(self, request, pk=None):
        """
        Assign workout week to user (Admin only)
        Acepta week_template_id en el body
        """
        user = get_object_or_404(User, pk=pk)
        
        # Usar el serializer de creación
        serializer = UserWeekAssignmentCreateSerializer(
            data=request.data,
            context={'user': user}
        )
        
        if serializer.is_valid():
            # El serializer maneja la creación y desactivación de asignaciones anteriores
            assignment = serializer.save()
            
            # Retornar con el serializer completo
            response_serializer = UserWeekAssignmentSerializer(assignment)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def my_custom_days(self, request):
        """Get current user's custom workout days"""
        custom_days = UserCustomWorkoutDay.objects.filter(
            user=request.user,
            is_active=True
        ).order_by('day_order')
        serializer = UserCustomWorkoutDaySerializer(custom_days, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdmin], url_path='custom-days')
    def add_custom_day(self, request, pk=None):
        """Add custom workout day for user (Admin only)"""
        user = get_object_or_404(User, pk=pk)
        serializer = UserCustomWorkoutDaySerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(user=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def my_custom_exercises(self, request):
        """Get current user's custom exercise configurations"""
        custom_configs = UserCustomExerciseConfig.objects.filter(
            user=request.user,
            is_active=True
        )
        serializer = UserCustomExerciseConfigSerializer(custom_configs, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdmin], url_path='custom-exercises')
    def add_custom_exercise(self, request, pk=None):
        """Add custom exercise config for user (Admin only)"""
        user = get_object_or_404(User, pk=pk)
        serializer = UserCustomExerciseConfigSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(user=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)