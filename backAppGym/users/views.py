from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from core.permissions import IsAdmin
from assignments.models import UserWeekAssignment  # NUEVO IMPORT
from .serializers import (
    UserSerializer,
    UserRegistrationSerializer,
    UserDetailSerializer,
    CustomTokenObtainPairSerializer
)

User = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):
    """Vista personalizada para obtener JWT token con información del usuario"""
    serializer_class = CustomTokenObtainPairSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for user management
    Admin only can list/update/delete users
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_permissions(self):
        # Register and me endpoints are accessible
        if self.action in ['register', 'create']:
            permission_classes = [AllowAny]
        elif self.action == 'me':
            permission_classes = [IsAuthenticated]
        else:
            # Admin only for other actions
            permission_classes = [IsAdmin]
        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return UserDetailSerializer
        elif self.action in ['register', 'create']:
            return UserRegistrationSerializer
        return UserSerializer
    
    # MÉTODO ACTUALIZADO - Agrega info de asignaciones
    def list(self, request):
        """
        Listar usuarios con información de asignación actual
        """
        users = User.objects.filter(is_active=True).order_by('email')
        
        users_data = []
        for user in users:
            # Obtener asignación activa del usuario
            try:
                assignment = UserWeekAssignment.objects.get(
                    user=user,
                    is_active=True
                )
                current_assignment = {
                    'week_template_name': assignment.week_template.name,
                    'start_date': assignment.start_date.strftime('%Y-%m-%d')
                }
            except UserWeekAssignment.DoesNotExist:
                current_assignment = None
            
            # Serializar datos básicos del usuario
            user_serializer = self.get_serializer(user)
            user_data = user_serializer.data
            
            # Agregar info de asignación
            user_data['current_assignment'] = current_assignment
            
            users_data.append(user_data)
        
        return Response(users_data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """Get current user profile"""
        serializer = UserDetailSerializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        """Register new user"""
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                UserSerializer(user).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # MÉTODO NUEVO - Stats de usuarios (opcional pero útil)
    @action(detail=False, methods=['get'], permission_classes=[IsAdmin])
    def stats(self, request):
        """
        Obtener estadísticas de usuarios
        """
        total_users = User.objects.filter(is_active=True).count()
        users_with_assignment = UserWeekAssignment.objects.filter(
            is_active=True
        ).values('user').distinct().count()
        
        return Response({
            'total_users': total_users,
            'users_with_assignment': users_with_assignment,
            'users_without_assignment': total_users - users_with_assignment
        })