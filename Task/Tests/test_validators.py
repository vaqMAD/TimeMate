# Python imports
import uuid
# Django Imports
from django.test import TestCase
from django.contrib.auth import get_user_model
# DRF imports
from rest_framework.serializers import ValidationError
# Internal imports
from TimeMate.Utils.test_helpers import get_error_code
from Task.models import Task
from Task.validators import unique_owner_for_task_name, get_task_or_raise, validate_task_ownership
from Task.validators import VALIDATION_ERROR_CODE_UNIQUE_TASK_NAME, VALIDATION_ERROR_CODE_TASK_NOT_FOUND, \
    VALIDATION_ERROR_CODE_TASK_INVALID_OWNER

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

        errors = context.exception.detail
        self.assertEqual(get_error_code(errors), VALIDATION_ERROR_CODE_UNIQUE_TASK_NAME)
        self.assertIn(self.task_name, str(errors))
        self.assertIn(self.user.username, str(errors))


class GetTaskOrRaiseValidatorTests(TestCase):
    def setUp(self):
        # User objects related set up
        self.user = User.objects.create_user(username='testuser', email='<EMAIL>', password='<PASSWORD>')
        # Setup task
        self.task = Task.objects.create(name='Test Task', owner=self.user)

    def test_get_task_or_raise_valid_task(self):
        """
        Ensure that get_task_or_raise returns the correct task when the task ID exists.
        """
        fetched_task = get_task_or_raise(self.task.id)
        self.assertEqual(fetched_task, self.task)

    def test_get_task_or_raise_invalid_task(self):
        """
        Ensure that get_task_or_raise raises an error when the task ID does not exist.
        """
        invalid_task_id = uuid.uuid4()
        with self.assertRaises(ValidationError) as context:
            get_task_or_raise(invalid_task_id)

        error_msg = context.exception.detail[0]
        self.assertEqual(error_msg.code, VALIDATION_ERROR_CODE_TASK_NOT_FOUND)


class ValidateTaskOwnershipTests(TestCase):
    def setUp(self):
        # User objects related set up
        self.user = User.objects.create_user(username='testuser', email='<EMAIL>', password='<PASSWORD>')
        self.not_owner_user = User.objects.create_user(username='not_owner', email='<EMAIL>', password='<PASSWORD>')
        # Data set up
        self.task = Task.objects.create(name='Test Task', owner=self.user)

    def test_validate_task_ownership_success(self):
        """
        Ensure validate_task_ownership returns None when the task is owned by the user.
        """
        fetched_task = validate_task_ownership(self.task, self.user)
        self.assertEqual(fetched_task, self.task)

    def test_validate_task_ownership_failure(self):
        """
        Ensure validate_task_ownership raises ValidationError when the task is not owned by the user.
        """
        with self.assertRaises(ValidationError) as context:
            validate_task_ownership(self.task, self.not_owner_user)

        error_msg = context.exception.detail[0]
        self.assertEqual(error_msg.code, VALIDATION_ERROR_CODE_TASK_INVALID_OWNER)

    def test_validate_task_ownership_invalid_task(self):
        """
        Ensures validate_task_ownership raises ValidationError when the task ID does not exist.
        """
        invalid_task_id = uuid.uuid4()
        with self.assertRaises(ValidationError) as context:
            validate_task_ownership(invalid_task_id, self.user)

        error_msg = context.exception.detail[0]
        self.assertEqual(error_msg.code, VALIDATION_ERROR_CODE_TASK_NOT_FOUND)
