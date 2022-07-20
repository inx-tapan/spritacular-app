from rest_framework import permissions


class IsOwnerOrAdmin(permissions.BasePermission):
    message = "You must be the owner of this object."
    my_safe_methods = ['GET', 'PUT', 'PATCH', 'POST']

    def has_permission(self, request, view):
        return request.method in self.my_safe_methods

    def has_object_permission(self, request, view, obj):
        return obj if request.user.is_superuser else obj == request.user


class IsObjectOwnerOrAdmin(permissions.BasePermission):
    message = "You must be the owner of this object."

    def has_permission(self, request, view):
        return request.user

    def has_object_permission(self, request, view, obj):
        return obj if request.user.is_superuser else obj.user == request.user


class IsAdminOrTrained(permissions.BasePermission):
    message = "You must be a trained or a admin user."

    def has_permission(self, request, view):
        return bool(request.user.is_superuser or request.user.is_trained)

    def has_object_permission(self, request, view, obj):
        self.message = "You cannot vote your own observation."
        return obj.user != request.user


class IsAdmin(permissions.BasePermission):
    message = "You must be a admin user."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)
