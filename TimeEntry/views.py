# DRF imports
from rest_framework import generics
# Internal imports
from .models import TimeEntry
from .serializers import TimeEntryCreateSerializer, TimeEntryListSerializer
from TimeMate.Utils.pagination import DefaultPagination


# TODO [InProgress] : Check structure of the code, whether it meets Django standards
# TODO [InProgress] : Add  unit and integration tests for both GET and POST views.
# TODO [InProgress] : Think about whether structure of the GET response is appropriate.
class TimeEntryListCreateView(generics.ListCreateAPIView):
    pagination_class = DefaultPagination

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return TimeEntryCreateSerializer
        return TimeEntryListSerializer

    def get_queryset(self):
        return TimeEntry.objects.filter(owner=self.request.user)
