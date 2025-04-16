# Django imports
import django_filters

class TimeEntryFilter(django_filters.FilterSet):
    start_time = django_filters.IsoDateTimeFromToRangeFilter()
    end_time  = django_filters.IsoDateTimeFromToRangeFilter()
    task = django_filters.CharFilter(field_name='task__name', lookup_expr='icontains')