from django.urls import path
from .views import UserAssignmentViewSet

urlpatterns = [
    # User's own assignments
    path('my-assignment/', UserAssignmentViewSet.as_view({'get': 'my_assignment'}), name='my-assignment'),
    path('my-week-info/', UserAssignmentViewSet.as_view({'get': 'my_week_info'}), name='my-week-info'),
    path('renew-my-week/', UserAssignmentViewSet.as_view({'post': 'renew_my_week'}), name='renew-my-week'),
    path('my-custom-days/', UserAssignmentViewSet.as_view({'get': 'my_custom_days'}), name='my-custom-days'),
    path('my-custom-exercises/', UserAssignmentViewSet.as_view({'get': 'my_custom_exercises'}), name='my-custom-exercises'),
    
    # Admin endpoints for user management
    path('users/<int:pk>/assign-week/', UserAssignmentViewSet.as_view({'post': 'assign_week'}), name='assign-week'),
    path('users/<int:pk>/custom-days/', UserAssignmentViewSet.as_view({'post': 'add_custom_day'}), name='add-custom-day'),
    path('users/<int:pk>/custom-exercises/', UserAssignmentViewSet.as_view({'post': 'add_custom_exercise'}), name='add-custom-exercise'),
]