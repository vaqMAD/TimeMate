# DRF imports
from rest_framework import generics
# Internal imports
from .models import TimeEntry
from .serializers import TimeEntryCreateSerializer, TimeEntryListSerializer

# TODO [InProgress] : Check structure of the code, whether it meets Django standards
# TODO [InProgress] : Add  unit and integration tests for both GET and POST views.
# TODO [InProgress] : Think about whether structure of the GET response is appropriate.
class TimeEntryListCreateView(generics.ListCreateAPIView):

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return TimeEntryCreateSerializer
        return TimeEntryListSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        # Pass request and user to the serializer context
        context["request"] = self.request
        return context

    def get_queryset(self):
        return TimeEntry.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
