# DRF imports
from rest_framework import generics
# Internal imports
from .models import TimeEntry
from .serializers import TimeEntryCreateSerializer, TimeEntryListSerializer, TimeEntryDetailSerializer
from TimeMate.Utils.pagination import DefaultPagination
from TimeMate.Permissions.owner_permissions import IsObjectOwner


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

# # TODO [InProgress/NOTE] : This test class is a Work In Progress.
# The existing tests are under active development and are subject to further reviews and refinements.
class TimeEntryDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsObjectOwner]
    serializer_class = TimeEntryDetailSerializer

    def get_queryset(self):
        pk = self.kwargs.get("pk")
        return TimeEntry.objects.filter(pk=pk)