# Django imports
from django.db.models import Prefetch
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models.functions import TruncDate
# DRF imports
from rest_framework.filters import OrderingFilter
from rest_framework import generics
# Internal imports
from Task.models import Task
from .models import TimeEntry
from .serializers import (
    TimeEntryCreateSerializer,
    TimeEntryListSerializer,
    TimeEntryDetailSerializer,
    TimeEntryUpdateSerializer,
    TaskWithTimeEntriesSerializer,
    TimeEntryByDaySerializer,
)
from TimeMate.Utils.pagination import DefaultPagination
from .filters import TimeEntryFilter
from TimeMate.Permissions.owner_permissions import IsObjectOwner
from TimeMate.Utils.view_helpers import swagger_safe_queryset
from TimeMate.Utils.mixins import CacheListMixin
from .time_entry_spectacular_extensions import (
    TIME_ENTRY_LIST_CREATE_SCHEMA,
    TIME_ENTRY_DETAIL_SCHEMA,
    TASK_WITH_ENTRIES_SCHEMA,
    TIME_ENTRY_BY_DATE_SCHEMA,
)


class TimeEntryBaseView(generics.GenericAPIView):
    queryset = TimeEntry.objects.none()
    pagination_class = DefaultPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = TimeEntryFilter
    ordering_fields = ['start_time', 'end_time', 'task__name', 'duration']


@TIME_ENTRY_LIST_CREATE_SCHEMA
class TimeEntryListCreateView(CacheListMixin, TimeEntryBaseView, generics.ListCreateAPIView):
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return TimeEntryCreateSerializer
        return TimeEntryListSerializer

    @swagger_safe_queryset
    def get_queryset(self):
        return TimeEntry.objects.filter(owner=self.request.user).select_related('task', 'owner', 'task__owner')


@TIME_ENTRY_DETAIL_SCHEMA
class TimeEntryDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsObjectOwner]

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return TimeEntryUpdateSerializer
        return TimeEntryDetailSerializer

    def get_queryset(self):
        pk = self.kwargs.get("pk")
        return TimeEntry.objects.filter(pk=pk).select_related('task', 'owner')


@TASK_WITH_ENTRIES_SCHEMA
class TimeEntriesByTaskListView(CacheListMixin, TimeEntryBaseView, generics.ListAPIView):
    serializer_class = TaskWithTimeEntriesSerializer
    filterset_class = None
    ordering_fields = []

    @swagger_safe_queryset
    def get_queryset(self):
        task_qs = Task.objects.filter(owner=self.request.user).select_related('owner')

        time_entries_qs = TimeEntry.objects.order_by('task__name')

        return task_qs.prefetch_related(
            Prefetch('time_entries', queryset=time_entries_qs)
        )


@TIME_ENTRY_BY_DATE_SCHEMA
class TimeEntryByDateListView(CacheListMixin, TimeEntryBaseView, generics.ListAPIView):
    serializer_class = TimeEntryByDaySerializer
    ordering_fields = TimeEntryBaseView.ordering_fields + ['day']

    @swagger_safe_queryset
    def get_queryset(self):
        return (TimeEntry.objects.filter(owner=self.request.user).
                annotate(day=TruncDate('end_time')).
                order_by('-day', '-end_time').
                select_related('task', 'owner', 'task__owner'))
