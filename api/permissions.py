from rest_framework.permissions import BasePermission, SAFE_METHODS

# SAFE_METHODS = ("GET", "HEAD", "OPTIONS")  # oxumaq üçün icazə verilən metodlar

class IsOwnerOrReadOnly(BasePermission):

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the object.
        return obj.author == request.user