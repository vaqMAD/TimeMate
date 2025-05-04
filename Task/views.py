# DRF imports
from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
# Internal imports
from .models import Task
from .serializers import TaskCreateSerializer, TaskDetailSerializer, TaskListSerializer, TaskUpdateSerializer
from TimeMate.Permissions.owner_permissions import IsObjectOwner
from TimeMate.Utils.pagination import DefaultPagination
from .filters import TaskFilter
from .task_spectacular_extensions import (
    TASK_DETAIL_SCHEMA,
    TASK_LIST_CREATE_SCHEMA,
)

@TASK_DETAIL_SCHEMA
class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsObjectOwner]
    serializer_class = TaskDetailSerializer

    def get_queryset(self):
        pk = self.kwargs.get("pk")
        return Task.objects.filter(pk=pk)

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return TaskUpdateSerializer
        return TaskDetailSerializer

@TASK_LIST_CREATE_SCHEMA
class TaskListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsObjectOwner]
    pagination_class = DefaultPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = TaskFilter
    ordering_fields = ['created_at', 'name']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return TaskCreateSerializer
        return TaskListSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Task.objects.none()

        return Task.objects.filter(owner=self.request.user)
