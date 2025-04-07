# Django imports
from django.urls import reverse
from django.contrib.auth import get_user_model
# DRF imports
from rest_framework import status
from rest_framework.test import APITestCase
# Internal imports
from Task.models import Task
from TimeEntry.models import TimeEntry

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
            start_time='2025-10-01T08:00:00Z',
            end_time='2025-10-01T10:00:00Z'
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
        self.assertEqual(self.time_entry.start_time.isoformat(), payload['start_time'].replace('Z', '+00:00'))
        self.assertEqual(self.time_entry.end_time.isoformat(), payload['end_time'].replace('Z', '+00:00'))

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
        self.assertIn("must be greater", str(response.data['non_field_errors'][0]))

    def test_update_time_entry_non_owner(self):
        """
        Ensure that a non-owner cannot update the time entry.
        """
        self.client.force_authenticate(user=self.other_user)
        payload = {
            "start_time": "2023-10-01T10:30:00Z",
            "end_time": "2023-10-01T11:30:00Z"
        }
        response = self.client.patch(self.detail_url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

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
