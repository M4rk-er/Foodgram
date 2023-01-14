from rest_framework import permissions

class UserPermissions(permissions.BasePermission):
    
    def has_object_permission(self, request, view, obj):
        if view.action == 'retrieve':
            return request.user.is_authenticated
        return True
        