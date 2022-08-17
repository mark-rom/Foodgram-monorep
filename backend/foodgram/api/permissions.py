from rest_framework.permissions import SAFE_METHODS, BasePermission


class AuthorOrReadOnly(BasePermission):
    """Разрешает небезопасные методы запроса к объекту только его автору."""
    def has_object_permission(self, request, view, obj):
        return (obj.author == request.user or request.method in SAFE_METHODS)
