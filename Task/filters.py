# Django imports
import django_filters
# Internal imports
from .models import Task


class TaskFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")
    created_at = django_filters.DateTimeFromToRangeFilter(field_name='created_at')
