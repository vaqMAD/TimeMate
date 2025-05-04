# Django imports
from django.urls import path
# Internal imports
from .views import TaskCreateView, TaskDetailView, TaskListCreateView

urlpatterns = [
    path('', TaskListCreateView.as_view(), name='task_list_create'),
    # Tę ścieżkę url również usuniemy
    path('create/', TaskCreateView.as_view(), name='task_create'),
    path('<uuid:pk>/', TaskDetailView.as_view(), name='task_detail'),
]
