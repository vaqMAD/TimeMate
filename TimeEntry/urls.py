# Django imports
from django.urls import path, include
# Internal imports
from .views import (
    TimeEntryListCreateView,
    TimeEntryDetailView,
    TimeEntrySortedByTaskNameListView
)

urlpatterns = [
    # TBA Tests purposes only
    path('', TimeEntryListCreateView.as_view(), name='time_entry_list_create'),
    path('<uuid:pk>/', TimeEntryDetailView.as_view(), name='time_entry_detail'),
    path('sorted-by-task-name/', TimeEntrySortedByTaskNameListView.as_view(), name='time_entry_sorted_by_task_name'),
]