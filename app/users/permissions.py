from rest_framework import permissions


class IsOwnerOrAdmin(permissions.BasePermission):
    message = "You must be the owner of this object."
    my_safe_methods = ['GET', 'PUT', 'PATCH', 'POST']

    def has_permission(self, request, view):
        if request.method in self.my_safe_methods:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return obj
        else:
            return obj == request.user
