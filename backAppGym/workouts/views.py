from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from core.permissions import IsAdmin
from .models import (
    WorkoutDayTemplate,
    WorkoutDayExercise,
    WorkoutWeekTemplate,
    WorkoutWeekDay,
)
from .serializers import (
    WorkoutDayTemplateSerializer,
    WorkoutDayTemplateListSerializer,
    WorkoutDayExerciseSerializer,
    WorkoutWeekTemplateSerializer,
    WorkoutWeekTemplateListSerializer,
    WorkoutWeekDaySerializer,
)
from .services import WorkoutDayService


class WorkoutDayTemplateViewSet(viewsets.ModelViewSet):
    """
    CRUD for workout day templates
    Admin: full access
    Users: read-only
    """
    queryset = WorkoutDayTemplate.objects.filter(is_active=True).prefetch_related('exercises__exercise')
    serializer_class = WorkoutDayTemplateSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['type']
    search_fields = ['name']
    ordering_fields = ['type', 'name', 'created_at']
    ordering = ['type']
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAdmin]
        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return WorkoutDayTemplateListSerializer
        return WorkoutDayTemplateSerializer
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdmin])
    def add_exercise(self, request, pk=None):
        """Add exercise to workout day"""
        workout_day = self.get_object()
        exercise_id = request.data.get('exercise_id')
        order = request.data.get('order')
        number_of_sets = request.data.get('number_of_sets', 3)
        
        try:
            workout_day_exercise = WorkoutDayService.add_exercise_to_day(
                workout_day.id,
                exercise_id,
                order,
                number_of_sets
            )
            serializer = WorkoutDayExerciseSerializer(workout_day_exercise)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['delete'], permission_classes=[IsAdmin], url_path='exercises/(?P<exercise_id>[^/.]+)')
    def remove_exercise(self, request, pk=None, exercise_id=None):
        """Remove exercise from workout day"""
        workout_day = self.get_object()
        try:
            workout_day_exercise = WorkoutDayExercise.objects.get(
                workout_day=workout_day,
                exercise_id=exercise_id,
                is_active=True
            )
            workout_day_exercise.is_active = False
            workout_day_exercise.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except WorkoutDayExercise.DoesNotExist:
            return Response(
                {'error': 'Exercise not found in this workout day'},
                status=status.HTTP_404_NOT_FOUND
            )


class WorkoutWeekTemplateViewSet(viewsets.ModelViewSet):
    """
    CRUD for workout week templates
    Admin: full access
    Users: read-only
    """
    queryset = WorkoutWeekTemplate.objects.filter(is_active=True).prefetch_related('days__workout_day')
    serializer_class = WorkoutWeekTemplateSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAdmin]
        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self):
        # ✅ FIX: SIEMPRE usar el serializer completo que incluye days
        # El frontend necesita el array completo de días para mostrar en el dropdown
        return WorkoutWeekTemplateSerializer
        
        # ANTES (causaba el problema):
        # if self.action == 'list':
        #     return WorkoutWeekTemplateListSerializer
        # return WorkoutWeekTemplateSerializer
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdmin])
    def add_day(self, request, pk=None):
        """Add workout day to week"""
        week_template = self.get_object()
        serializer = WorkoutWeekDaySerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(week_template=week_template)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['delete'], permission_classes=[IsAdmin], url_path='days/(?P<day_order>[^/.]+)')
    def remove_day(self, request, pk=None, day_order=None):
        """Remove day from week"""
        week_template = self.get_object()
        try:
            week_day = WorkoutWeekDay.objects.get(
                week_template=week_template,
                day_order=day_order,
                is_active=True
            )
            week_day.is_active = False
            week_day.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except WorkoutWeekDay.DoesNotExist:
            return Response(
                {'error': 'Day not found in this week'},
                status=status.HTTP_404_NOT_FOUND
            )