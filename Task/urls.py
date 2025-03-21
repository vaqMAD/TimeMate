# Django imports
from django.urls import path
# Internal imports
from .views import TaskCreateView, TaskDetailView, TaskListView

urlpatterns = [
    path('', TaskListView.as_view(), name='task_list'),
    path('create/', TaskCreateView.as_view(), name='task_create'),
    path('<uuid:pk>/', TaskDetailView.as_view(), name='task_detail'),
]
