from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from core.permissions import IsAdmin, IsOwnerOrAdmin
from users.models import User
from .models import UserWeekAssignment, UserCustomWorkoutDay, UserCustomExerciseConfig
from .serializers import (
    UserWeekAssignmentSerializer,
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
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdmin], url_path='assign-week')
    def assign_week(self, request, pk=None):
        """Assign workout week to user (Admin only)"""
        user = get_object_or_404(User, pk=pk)
        
        # Deactivate existing assignment
        UserWeekAssignment.objects.filter(user=user).update(is_active=False)
        
        # Create new assignment
        serializer = UserWeekAssignmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
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