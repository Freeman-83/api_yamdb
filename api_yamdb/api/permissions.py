from rest_framework import permissions

ROLES = ('auth_user', 'moderator', 'admin')


class AdminOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_staff)


class AuthorOrModeratorOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or request.user == 'moderator'
                or obj.author == request.user)
    # в моделях Review и Comments нужно использовать поле 'author'!!!
