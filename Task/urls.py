# Django imports
from django.urls import path
# Internal imports
from .views import TaskDetailView, TaskListCreateView

urlpatterns = [
    path('', TaskListCreateView.as_view(), name='task_list_create'),
    path('<uuid:pk>/', TaskDetailView.as_view(), name='task_detail'),
]
