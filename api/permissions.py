from rest_framework.permissions import BasePermission


class IsAdminOrReadOnly(BasePermission):

    def has_permission(self, request, view):

        # semua orang boleh lihat product
        if request.method in [
            'GET',
            'HEAD',
            'OPTIONS'
        ]:
            return True


        # hanya admin
        return (
            request.user.is_authenticated
            and request.user.is_staff
        )
    
class IsAdminOnly(BasePermission):

    def has_permission(self, request, view):

        return (
            request.user.is_authenticated
            and request.user.is_staff
        )