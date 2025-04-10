# Python imports
import uuid
from datetime import timedelta
# Django Imports
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
# DRF Imports
from rest_framework.test import APITestCase
# Internal imports
from TimeMate.Utils.utils import get_error_code
from TimeEntry.models import TimeEntry
from Task.models import Task
from TimeEntry.validators import VALIDATION_ERROR_CODE_INVALID_TIME_RANGE
from Task.validators import VALIDATION_ERROR_CODE_TASK_INVALID_OWNER

User = get_user_model()


class TimeEntryCreateTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='<EMAIL>', password='<PASSWORD>')
        self.other_user = User.objects.create_user(username='otheruser', email='<EMAIL>', password='<PASSWORD>')
        self.task = Task.objects.create(name='Test Task', owner=self.user)
        self.time_entry_sample_object = TimeEntry.objects.create(
            task=self.task,
            owner=self.user,
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(hours=1)
        )
        self.url = reverse('time_entry_list_create')

    def test_create_time_entry_valid_data(self):
        """
        Ensure we can create a new time entry object.
        The response should have status 201 and the returned task field must match the provided task ID
        """
        self.client.force_authenticate(user=self.user)
        valid_data = {
            'task': self.task.id,
            'start_time': timezone.now().isoformat(),
            'end_time': (timezone.now() + timedelta(hours=2)).isoformat()
        }
        response = self.client.post(self.url, data=valid_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['task'], self.task.id)
        self.assertEqual(TimeEntry.objects.count(), 2)
        self.assertEqual(response.data['owner']['username'], self.user.username)

    def test_time_entry_with_equal_start_and_end_times(self):
        """
        Ensure that creating a time entry with equal start_time and end_time returns a 400 error.
        The response should contain 'non_field_errors' indicating the invalid time range.
        """
        self.client.force_authenticate(user=self.user)
        invalid_date_time = timezone.now().isoformat()

        invalid_data = {
            'task': self.task.id,
            'start_time': invalid_date_time,
            'end_time': invalid_date_time  # start_time == end_time, invalid case
        }

        response = self.client.post(self.url, data=invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)
        errors = response.data['non_field_errors']
        self.assertEqual(get_error_code(errors), VALIDATION_ERROR_CODE_INVALID_TIME_RANGE)

    def test_create_time_entry_invalid_time_range(self):
        """
        Ensure that creating a time entry with start_time later than end_time returns a 400 error.
        The response should include appropriate validation error messages.
        """
        self.client.force_authenticate(user=self.user)
        invalid_data = {
            'task': self.task.id,
            'start_time': timezone.now(),
            'end_time': timezone.now() - timedelta(hours=1)  # invalid: end_time earlier than start_time
        }
        response = self.client.post(self.url, data=invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)
        errors = response.data['non_field_errors']
        self.assertEqual(get_error_code(errors), VALIDATION_ERROR_CODE_INVALID_TIME_RANGE)

    def test_owner_field_is_ignored_in_input(self):
        """
        Ensure that the owner field is ignored, and replaced with the current user.
        """
        self.client.force_authenticate(user=self.user)
        undesired_user = uuid.uuid4()

        data = {
            'task': self.task.id,
            'start_time': timezone.now().isoformat(),
            'end_time': (timezone.now() + timedelta(hours=1)).isoformat(),
            'owner': undesired_user,
        }

        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['owner']['username'], self.user.username)

    def test_create_time_entry_for_task_not_owned_by_user(self):
        """
        Ensure that creating a time entry for a task not owned by the current user returns a 400 error.
        """
        other_task = Task.objects.create(name='Other Task', owner=self.other_user)
        self.client.force_authenticate(user=self.user)
        data = {
            'task': other_task.id,
            'start_time': timezone.now().isoformat(),
            'end_time': (timezone.now() + timedelta(hours=1)).isoformat(),
        }
        response = self.client.post(self.url, data=data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        errors = response.data['task']
        self.assertEqual(get_error_code(errors), VALIDATION_ERROR_CODE_TASK_INVALID_OWNER)
