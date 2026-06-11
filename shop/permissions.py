from rest_framework import permissions

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Разрешает доступ администратору или владельцу объекта.
    Предполагает, что у объекта есть поле 'user'.
    """
    def has_object_permission(self, request, view, obj):
        # Проверяем, авторизован ли пользователь
        if not request.user or not request.user.is_authenticated:
            return False
            
        # Админ имеет доступ всегда
        if request.user.is_staff:
            return True
            
        # Владелец имеет доступ, если объект принадлежит ему
        return obj.user == request.user


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Разрешает чтение всем (GET, HEAD, OPTIONS),
    но изменение (POST, PUT, PATCH, DELETE) — только администратору.
    """
    def has_permission(self, request, view):
        # SAFE_METHODS — это GET, HEAD, OPTIONS
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Разрешаем запись, только если пользователь авторизован и является админом
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.is_staff
        )