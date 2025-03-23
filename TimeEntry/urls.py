# Django imports
from django.urls import path, include
# Internal imports
from .views import TimeEntryCreateView

urlpatterns = [
    # TBA Tests purposes only
    path('create/', TimeEntryCreateView.as_view(), name='time_entry_create'),
]

# TODO:
# 1. Change URLs patterns.