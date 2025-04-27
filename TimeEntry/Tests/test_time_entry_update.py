# Django imports
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.urls import reverse
from django.contrib.auth import get_user_model
# DRF imports
from rest_framework import status
from rest_framework.test import APITestCase
# Internal imports
from TimeMate.Utils.utils import get_error_code
from Task.models import Task
from TimeEntry.models import TimeEntry
from TimeEntry.validators import VALIDATION_ERROR_CODE_INVALID_TIME_RANGE
from Task.validators import VALIDATION_ERROR_CODE_TASK_INVALID_OWNER
from TimeMate.Permissions.owner_permissions import PERMISSION_ERROR_CODE_NOT_TASK_OWNER

User = get_user_model()


class TimeEntryUpdateTests(APITestCase):
    def setUp(self):
        # Set up user objects for testing
        self.user = User.objects.create_user(username='user1', password='<PASSWORD>', email='<EMAIL>')
        self.other_user = User.objects.create_user(username='user2', password='<PASSWORD>', email='<EMAIL>')

        # Create Task instance
        self.task = Task.objects.create(name="Sample Task", owner=self.user)

        # Create TimeEntry istance
        self.time_entry = TimeEntry.objects.create(
            task=self.task,
            owner=self.user,
            start_time=timezone.now(),
            end_time=timezone.now() + timezone.timedelta(hours=1)
        )

        self.detail_url = reverse('time_entry_detail', kwargs={'pk': self.time_entry.id})

    def test_update_time_entry_success(self):
        """
        Ensure that owner can successfully update time entry.
        """

        self.client.force_authenticate(user=self.user)
        payload = {
            "start_time": "2025-10-01T09:00:00Z",
            "end_time": "2025-10-01T11:00:00Z"
        }

        response = self.client.patch(self.detail_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.time_entry.refresh_from_db()

        # Parse payload datetimes to compare with the values from the database.
        expected_start_time = parse_datetime(payload['start_time'])
        expected_end_time = parse_datetime(payload['end_time'])

        self.assertEqual(self.time_entry.start_time, expected_start_time)
        self.assertEqual(self.time_entry.end_time, expected_end_time)

    def test_update_time_entry_invalid_times(self):
        """
        Ensure that providing invalid time ranges returns a 400 error.
        """

        self.client.force_authenticate(user=self.user)
        payload = {
            "start_time": "2025-10-01T11:00:00Z",
            "end_time": "2025-10-01T09:00:00Z"
        }
        response = self.client.patch(self.detail_url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)
        error_message = response.data['non_field_errors']
        self.assertEqual(get_error_code(error_message), VALIDATION_ERROR_CODE_INVALID_TIME_RANGE)

    def test_update_time_entry_non_owner(self):
        """
        Ensure that a non-owner cannot update the time entry.
        """
        self.client.force_authenticate(user=self.other_user)
        payload = {
            "start_time": "2025-10-01T10:30:00Z",
            "end_time": "2025-10-01T11:30:00Z"
        }
        response = self.client.patch(self.detail_url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        error_detail = response.data['detail']
        self.assertEqual(get_error_code(error_detail), PERMISSION_ERROR_CODE_NOT_TASK_OWNER)

    def test_update_protected_fields(self):
        """
        Ensure that fields like 'owner' cannot be updated.
        """

        self.client.force_authenticate(user=self.user)
        payload = {
            "owner": self.other_user.id
        }
        response = self.client.patch(self.detail_url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.time_entry.refresh_from_db()
        # Ensure the owner has not changed
        self.assertEqual(self.time_entry.owner, self.user)

    def test_update_time_entry_with_task_owner_success(self):
        """
        Ensure that the owner of the task can successfully update the task for a time entry.
        """
        self.client.force_authenticate(user=self.task.owner)
        other_task_owned_by_user = Task.objects.create(name="Other Task", owner=self.user)
        payload = {
            'task': str(other_task_owned_by_user.id),
            "start_time": "2025-10-01T09:00:00Z",
            "end_time": "2025-10-01T11:00:00Z"
        }
        response = self.client.patch(self.detail_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_time_entry_with_task_owner_invalid_task_owner(self):
        """
        Ensure that attempting to update a time entry with a task assigned to a different owner
        returns a 400 error.
        """

        self.client.force_authenticate(user=self.task.owner)
        task_owned_by_other_user = Task.objects.create(name="Other Task", owner=self.other_user)

        payload = {
            'task': str(task_owned_by_other_user.id),
            "start_time": "2025-10-01T09:00:00Z",
            "end_time": "2025-10-01T11:00:00Z"
        }
        response = self.client.patch(self.detail_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        error_message = response.data['task']
        self.assertEqual(get_error_code(error_message), VALIDATION_ERROR_CODE_TASK_INVALID_OWNER)
