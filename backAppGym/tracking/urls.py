from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WorkoutLogViewSet, SetLogViewSet

router = DefaultRouter()
router.register(r'workouts', WorkoutLogViewSet, basename='workout-log')
router.register(r'sets', SetLogViewSet, basename='set-log')

urlpatterns = [
    path('', include(router.urls)),
]