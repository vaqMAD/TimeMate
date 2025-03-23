# DRF imports
from rest_framework import generics
# Internal imports
from .serializers import TimeEntryCreateSerializer


class TimeEntryCreateView(generics.CreateAPIView):
    serializer_class = TimeEntryCreateSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        # Pass request and user to the serializer context
        context["request"] = self.request
        return context
