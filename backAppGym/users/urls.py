from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import UserViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    # JWT Authentication (no requieren autenticación)
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Registration (no requiere autenticación)
    path('register/', UserViewSet.as_view({'post': 'register'}), name='register'),
    
    # User profile (requiere autenticación)
    path('me/', UserViewSet.as_view({'get': 'me'}), name='me'),
    
    # User management (admin only)
    path('', include(router.urls)),
]