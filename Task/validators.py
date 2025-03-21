# DRF imports
from rest_framework import serializers
# Internal imports
from .models import Task


def unique_owner_for_task_name(owner, task_name):
    """
    Checks if the owner already has an object with the given task name
    """
    if Task.objects.filter(owner=owner, name=task_name).exists():
        raise serializers.ValidationError(
            f"This user: {owner.username}, already has an object with the same name: {task_name}"
        )
