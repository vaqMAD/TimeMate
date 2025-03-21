# DRF imports
from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
# Internal imports
from .models import Task
from .serializers import TaskCreateSerializer, TaskDetailSerializer, TaskListSerializer, TaskUpdateSerializer
from TimeMate.Permissions.owner_permissions import IsObjectOwner
from .pagination import TaskPagination
from .filters import TaskFilter


class TaskCreateView(generics.CreateAPIView):
    serializer_class = TaskCreateSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        # Pass request and user to the serializer context
        context["request"] = self.request
        return context


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsObjectOwner]
    serializer_class = TaskDetailSerializer

    def get_queryset(self):
        pk = self.kwargs.get("pk")
        return Task.objects.filter(pk=pk)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        # Pass request and user to the serializer context
        context["request"] = self.request
        return context

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return TaskUpdateSerializer
        return TaskDetailSerializer


class TaskListView(generics.ListAPIView):
    permission_classes = [IsObjectOwner]
    serializer_class = TaskListSerializer
    pagination_class = TaskPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = TaskFilter
    ordering_fields = ['created_at', 'name']

    def get_queryset(self):
        return Task.objects.filter(owner=self.request.user)