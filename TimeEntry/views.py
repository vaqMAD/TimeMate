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

class TimeEntryBaseView:
    pagination_class = DefaultPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = TimeEntryFilter
    ordering_fields = ['start_time', 'end_time', 'task', 'duration']

class TimeEntryListCreateView(TimeEntryBaseView, generics.ListCreateAPIView):

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return TimeEntryCreateSerializer
        return TimeEntryListSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return TimeEntry.objects.none()

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


class TimeEntriesByTaskListView(TimeEntryBaseView, generics.ListAPIView):
    serializer_class = TaskWithTimeEntriesSerializer
    ordering_fields = ['start_time', 'end_time', 'task__name', 'duration']

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return TimeEntry.objects.none()
        task_qs = Task.objects.filter(owner=self.request.user)

        time_entries_qs = TimeEntry.objects.order_by('task__name')

        return task_qs.prefetch_related(
            Prefetch('time_entries', queryset=time_entries_qs)
        )

class  TimeEntryByDateVListView(TimeEntryBaseView, generics.ListAPIView):
    serializer_class = TimeEntryByDaySerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return TimeEntry.objects.none()
        return (TimeEntry.objects.filter(owner=self.request.user).
                annotate(day=TruncDate('end_time')).
                order_by('-day', '-end_time').
                select_related('task'))