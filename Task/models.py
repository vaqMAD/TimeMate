# Python imports
import uuid
# Django imports
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinLengthValidator, MaxLengthValidator

User = get_user_model()


class Task(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, validators=[MinLengthValidator(2), MaxLengthValidator(200)])
    description = models.TextField(
        max_length=1000,
        validators=[MinLengthValidator(2), MaxLengthValidator(1000)],
        blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')

    class Meta:
        constraints = [
            # Applying uniqueness validation to the name and owner fields at the database level
            models.UniqueConstraint(fields=['name', 'owner'], name='unique_task_name_per_owner'),
        ]

        indexes = [
            models.Index(fields=['owner']),
            models.Index(fields=['name'])
        ]

        ordering = ['name']

    def __str__(self):
        return f"{self.name} - {self.owner}"
