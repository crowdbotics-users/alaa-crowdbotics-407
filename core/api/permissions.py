from rest_framework import permissions

from core.images.models import Image


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        """
        Object-level permission to only allow owners of an object to edit it.
        Assumes the model instance has an `owner` attribute.
        """
        if request.method in permissions.SAFE_METHODS:
            return True

        if isinstance(obj, Image):
            return request.user.id == obj.creator.owner.id
        return request.user.id == obj.owner.id
