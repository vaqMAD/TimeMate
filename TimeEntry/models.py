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
    duration = models.DurationField(editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Time entries"
        constraints = [
            # Ensures that the value of the `end_time` field is greater than the value of the `start_time` field.
            models.CheckConstraint(
                check=models.Q(end_time__gt=models.F('start_time')),
                name='end_time_gt_start_time',
                violation_error_message="Value for `end_time` field must be after `start_time`."
            )
        ]

        indexes = [
            models.Index(fields=['owner']),
            models.Index(fields=['task']),
            models.Index(fields=['start_time']),
            models.Index(fields=['end_time']),
            models.Index(fields=['duration']),
        ]

        ordering = ['-end_time']

    def save(self, *args, **kwargs):
        # Calculate the duration by subtracting start_time from end_time
        self.duration = self.end_time - self.start_time
        super().save(*args, **kwargs)

    def __str__(self):
        return f"TimeEntry for {self.task.name} ({self.start_time} - {self.end_time})"
