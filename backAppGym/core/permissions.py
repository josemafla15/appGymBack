from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """Only admin users can access"""
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role == 'ADMIN'
        )


class IsOwnerOrAdmin(permissions.BasePermission):
    """Owner can read, admin can do anything"""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Admin can do anything
        if request.user.role == 'ADMIN':
            return True
        
        # Check if object has 'user' attribute
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        return False


class ReadOnly(permissions.BasePermission):
    """Read-only access"""
    
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS