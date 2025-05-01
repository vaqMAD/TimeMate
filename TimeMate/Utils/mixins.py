# Django imports
from django.core.cache import cache
# DRF imports
from rest_framework.response import Response
# Internal imports
from TimeMate.Serializers.user_serializers import UserSerializer

class OwnerRepresentationMixin:
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Check if the instance has an `owner`
        if hasattr(instance, 'owner'):
            # Return owner field as a nested serialized object, not as an ID
            representation['owner'] = UserSerializer(instance.owner).data
        return representation


class CacheListMixin:
    cache_timeout = 300

    def list(self, request, *args, **kwargs):
        key = self.get_cache_key(request)
        cached_data = cache.get(key)
        if cached_data is not None:
            return Response(cached_data)
        response = super().list(request, *args, **kwargs)
        cache.set(key, response.data, self.cache_timeout)
        return response

    def get_cache_key(self, request):
        params = request.query_params.urlencode()
        return f'{self.__class__.__name__}:user={request.user.id}:{params}'