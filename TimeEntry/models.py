# Python imports
import uuid
# Django imports
from django.db import models
from django.contrib.auth import get_user_model
# Internal imports
from Task.models import Task

User = get_user_model()


class TimeEntry(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='time_entries')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='time_entries')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['owner']),
            models.Index(fields=['task']),
            models.Index(fields=['start_time']),
            models.Index(fields=['end_time']),
        ]

        ordering = ['name', '-start_time']

    def __str__(self):
        return f"TimeEntry for {self.task.name} ({self.start_time} - {self.end_time})"
