# Django imports
from django.core.cache import cache
# DRF imports
from rest_framework.response import Response
# Internal imports
from TimeMate.Serializers.user_serializers import UserSerializer

class OwnerRepresentationMixin:
    """
    Replace the `owner` ID with serialized user data.

    Overrides `to_representation` to embed a nested `owner` object
    using `UserSerializer` if the instance has an `owner` attribute.

    :param instance: Model instance being serialized.
    :type instance: models.Model
    :return: Serialized data dict with expanded `owner`.
    :rtype: dict
    """
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Check if the instance has an `owner`
        if hasattr(instance, 'owner'):
            # Return owner field as a nested serialized object, not as an ID
            representation['owner'] = UserSerializer(instance.owner).data
        return representation


class CacheListMixin:
    """
      Cache GET list responses based on user and query params.

      On `list()`, uses `get_cache_key` to fetch/set cached `.data`
      for up to `cache_timeout` seconds.

      Attributes:
          cache_timeout (int): Time in seconds to keep cached responses.

      :param request: DRF Request object.
      :type request: rest_framework.request.Request
      :return: Cached or fresh DRF Response.
      :rtype: rest_framework.response.Response
      """
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
        """
        Build cache key from view name, user ID, and query params.

        :param request: DRF Request object.
        :type request: rest_framework.request.Request
        :return: Unique cache key string.
        :rtype: str
        """
        params = request.query_params.urlencode()
        return f'{self.__class__.__name__}:user={request.user.id}:{params}'