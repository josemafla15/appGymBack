from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from datetime import datetime
from core.permissions import IsOwnerOrAdmin
from .models import WorkoutLog, SetLog
from .serializers import (
    WorkoutLogSerializer,
    WorkoutLogListSerializer,
    SetLogSerializer,
)


class WorkoutLogViewSet(viewsets.ModelViewSet):
    """
    CRUD for workout logs
    Users can only access their own logs
    """
    serializer_class = WorkoutLogSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['completed', 'date']
    ordering_fields = ['date', 'created_at']
    ordering = ['-date']
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return WorkoutLog.objects.filter(is_active=True).select_related('workout_day', 'user')
        return WorkoutLog.objects.filter(user=user, is_active=True).select_related('workout_day')
    
    def get_serializer_class(self):
        if self.action == 'list':
            return WorkoutLogListSerializer
        return WorkoutLogSerializer
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def add_set(self, request, pk=None):
        """Add set log to workout"""
        workout_log = self.get_object()
        serializer = SetLogSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(workout_log=workout_log)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['patch'])
    def mark_completed(self, request, pk=None):
        """Mark workout as completed"""
        workout_log = self.get_object()
        workout_log.completed = True
        workout_log.save()
        return Response({'status': 'Workout marked as completed'})
    
    @action(detail=False, methods=['get'])
    def history(self, request):
        """Get workout history with filters"""
        queryset = self.get_queryset()
        
        # Filter by date range
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        
        serializer = WorkoutLogListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get user workout statistics"""
        queryset = self.get_queryset()
        
        total_workouts = queryset.count()
        completed_workouts = queryset.filter(completed=True).count()
        total_sets = SetLog.objects.filter(
            workout_log__in=queryset,
            is_active=True
        ).count()
        
        return Response({
            'total_workouts': total_workouts,
            'completed_workouts': completed_workouts,
            'completion_rate': (completed_workouts / total_workouts * 100) if total_workouts > 0 else 0,
            'total_sets': total_sets,
        })


class SetLogViewSet(viewsets.ModelViewSet):
    """
    CRUD for set logs
    Users can only access their own set logs
    """
    serializer_class = SetLogSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return SetLog.objects.filter(is_active=True).select_related('exercise', 'workout_log')
        return SetLog.objects.filter(
            workout_log__user=user,
            is_active=True
        ).select_related('exercise', 'workout_log')