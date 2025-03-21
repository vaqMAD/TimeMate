# Django Imports
from django.test import TestCase
from django.contrib.auth import get_user_model
# DRF imports
from rest_framework.serializers import ValidationError
# Internal imports
from Task.models import Task
from Task.validators import unique_owner_for_task_name

User = get_user_model()


class UniqueOwnerForTaskNameValidatorTests(TestCase):
    def setUp(self):
        # User objects related set up
        self.user = User.objects.create_user(username='testuser', email='<EMAIL>', password='<PASSWORD>')
        # Data set up
        self.task_name = "Test Task"

    def test_validator_passes_when_task_does_not_exist(self):
        """
        Ensure that validation passes when no task with the given name exists for the user.
        """
        try:
            # Call validation when the task does not exist.
            unique_owner_for_task_name(self.user, self.task_name)
        except ValidationError:
            self.fail("ValidationError raised unexpectedly when task does not exist.")

    def test_validator_raises_error_when_task_exists(self):
        """
        Ensure that validation raises an error when a task with the given name already exists for the user.
        """
        # Create a task first.
        Task.objects.create(name=self.task_name, owner=self.user)

        with self.assertRaises(ValidationError) as context:
            # Call validation when the task exists.
            unique_owner_for_task_name(self.user, self.task_name)

        error_msg = str(context.exception)
        # Verify that the error message contains the task name and user's username.
        self.assertIn(self.task_name, error_msg)
        self.assertIn(self.user.username, error_msg)