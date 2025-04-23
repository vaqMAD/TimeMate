# Django imports
from django.db.models import (
    F,
    ExpressionWrapper,
    DurationField, Prefetch
)
from django_filters.rest_framework import DjangoFilterBackend
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
    TaskWithTimeEntriesSerializer
)
from TimeMate.Utils.pagination import DefaultPagination
from .filters import TimeEntryFilter
from TimeMate.Permissions.owner_permissions import IsObjectOwner


class TimeEntryListCreateView(generics.ListCreateAPIView):
    pagination_class = DefaultPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = TimeEntryFilter
    ordering_fields = ['start_time', 'end_time', 'task']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return TimeEntryCreateSerializer
        return TimeEntryListSerializer

    def get_queryset(self):
        return TimeEntry.objects.filter(owner=self.request.user).select_related('task', 'owner')


class TimeEntryDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsObjectOwner]

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return TimeEntryUpdateSerializer
        return TimeEntryDetailSerializer

    def get_queryset(self):
        pk = self.kwargs.get("pk")
        return TimeEntry.objects.filter(pk=pk).select_related('task', 'owner')

class TimeEntrySortedByTaskNameListView(generics.ListAPIView):
    serializer_class = TaskWithTimeEntriesSerializer
    pagination_class = DefaultPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = TimeEntryFilter
    ordering_fields = ['start_time', 'end_time', 'task__name', 'entries__duration']

    def get_queryset(self):
        task_qs = Task.objects.filter(owner=self.request.user)

        time_entries_qs = TimeEntry.objects.annotate(
            duration=ExpressionWrapper(
                F('end_time') - F('start_time'),
                output_field=DurationField()
            )
        ).order_by('task__name')

        return task_qs.prefetch_related(
            Prefetch('time_entries',queryset=time_entries_qs )
        )
