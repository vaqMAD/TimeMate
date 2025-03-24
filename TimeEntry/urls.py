# Django imports
from django.urls import path, include
# Internal imports
from .views import TimeEntryListCreateView

urlpatterns = [
    # TBA Tests purposes only
    path('', TimeEntryListCreateView.as_view(), name='time_entry_list_create'),
]

# TODO:
# 1. Change the list of the URL paths, so that it complies with REST standards