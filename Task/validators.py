# Validators error codes
VALIDATION_ERROR_CODE_UNIQUE_TASK_NAME = "unique_task_name"
VALIDATION_ERROR_CODE_TASK_NOT_FOUND = "task_not_found"
VALIDATION_ERROR_CODE_TASK_INVALID_OWNER = "task_invalid_owner"
# DRF imports
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
# Internal imports
from .models import Task


def unique_owner_for_task_name(owner, task_name):
    """
    Check for unique ownership of a task name.

    This function checks whether a task name provided by an owner already
    exists in the database. If the task name already exists under the specified
    owner, it raises a validation error. It helps maintain the uniqueness of
    task names within each owner's scope.

    :param owner: The user who owns the task.
    :type owner: User
    :param task_name: The name of the task to be checked for uniqueness.
    :type task_name: str
    :raises serializers.ValidationError: If the owner already has a task with
        the provided name.
    """
    if Task.objects.filter(owner=owner, name=task_name).exists():
        raise serializers.ValidationError(
            f"This user: {owner.username}, already has an object with the same name: {task_name}",
            code=VALIDATION_ERROR_CODE_UNIQUE_TASK_NAME
        )


def get_task_or_raise(task_value):
    """
    Retrieve a Task instance based on the given input or raise a validation error.

    This function attempts to resolve a task by ID or returns the input if it is
    already a Task instance. If a task with the specified ID is not found in the
    database, a validation error is raised.

    :param task_value: The task input, which can either be a Task instance or
        an ID corresponding to a Task object.
    :type task_value: Task | UUID

    :return: A Task instance resolved from either the provided ID or the task
        instance itself.
    :rtype: Task

    :raises serializers.ValidationError: If the task with the given ID does
        not exist in the database.
    """
    if isinstance(task_value, Task):
        return task_value

    try:
        task = Task.objects.get(id=task_value)
    except Task.DoesNotExist:
        raise serializers.ValidationError(
            "Task with given id does not exist",
            code=VALIDATION_ERROR_CODE_TASK_NOT_FOUND
        )
    return task


def validate_task_ownership(task_value, user):
    """
    Validates ownership of a task for a specific user and ensures
    that only the owner can proceed with accessing the task.

    This function retrieves a task using the provided task value,
    compares the ownership against the given user, and raises a
    ValidationError if the user does not own the task. If the
    validation passes, the task object is returned.

    :param task_value: The task input, which can either be a Task instance or
        an ID corresponding to a Task object.
    :type task_value: Task | UUID
    :param user: The user attempting to access the task
    :type user: Any relevant user object type
    :return: The validated task object
    :rtype: The type returned by the get_task_or_raise function

    :raises ValidationError: If the task is owned by someone other
        than the specified user
    """
    task = get_task_or_raise(task_value)

    if task.owner != user:
        raise ValidationError(
            "You do not have permission to access this task",
            code=VALIDATION_ERROR_CODE_TASK_INVALID_OWNER
        )

    return task
