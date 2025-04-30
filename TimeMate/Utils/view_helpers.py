# Python imports
from functools import wraps


def swagger_safe_queryset(fn):
    """
    Ensures safe execution of a get_queryset method during Swagger/OpenAPI
    schema generation (drf-spectacular).

    The problem:
        When introspecting views to generate a schema,
        Swagger libraries may want to call get_queryset() that requires a `user` object -
        which Swagger does not have access to.
    The solution:
        If `self.swagger_fake_view` is True, immediately return an
        empty queryset, bypassing business logic and DB access.
        Under normal operation, delegate to the original get_queryset().

    Requirements:
        - The view class must define either a `queryset` attribute
          or a `model` attribute from which `.none()` can be called.
    """
    @wraps(fn)
    def wrapper(self, *args, **kwargs):
        if getattr(self, 'swagger_fake_view', False):
            return self.model.objects.none()
        return fn(self, *args, **kwargs)

    return wrapper
