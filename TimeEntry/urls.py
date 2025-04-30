# Django imports
from django.urls import path, include
# Internal imports
from .views import (
    TimeEntryListCreateView,
    TimeEntryDetailView,
    TimeEntriesByTaskListView,
    TimeEntryByDateListView,
)

urlpatterns = [
    path('', TimeEntryListCreateView.as_view(), name='time_entry_list_create'),
    path('<uuid:pk>/', TimeEntryDetailView.as_view(), name='time_entry_detail'),
    path('sorted-by-task-name/', TimeEntriesByTaskListView.as_view(), name='time_entry_sorted_by_task_name'),
    path('sorted-by-date/', TimeEntryByDateListView.as_view(), name='time_entry_sorted_by_date'),
]
