from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WorkoutDayTemplateViewSet, WorkoutWeekTemplateViewSet

router = DefaultRouter()
router.register(r'days', WorkoutDayTemplateViewSet, basename='workout-day')
router.register(r'weeks', WorkoutWeekTemplateViewSet, basename='workout-week')

urlpatterns = [
    path('', include(router.urls)),
]