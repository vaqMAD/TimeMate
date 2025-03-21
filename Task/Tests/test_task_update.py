# Django imports
from django.urls import reverse
from django.contrib.auth import get_user_model
# DRF imports
from rest_framework import status
from rest_framework.test import APITestCase
# Internal imports
from Task.models import Task

User = get_user_model()


class TaskUpdateTests(APITestCase):
    def setUp(self):
        # Set up user objects for testing.
        self.user = User.objects.create_user(username='user1', password='<PASSWORD>', email='<EMAIL>')
        self.other_user = User.objects.create_user(username='user2', password='<PASSWORD>', email='<EMAIL>')

        # Create task instances for testing.
        self.task = Task.objects.create(name="Test Task", owner=self.user)
        self.other_task = Task.objects.create(name="Other Task", owner=self.user)

        # Set up the URL for the task detail view.
        self.detail_url = reverse('task_detail', kwargs={'pk': self.task.id})

    def test_update_task_success(self):
        """
        Ensure that the task owner can update the task's name and description.
        """
        self.client.force_authenticate(user=self.user)
        payload = {
            "name": "Updated Task Name",
            "description": "Updated description"
        }

        response = self.client.patch(self.detail_url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertEqual(self.task.name, payload['name'])
        self.assertEqual(self.task.description, payload['description'])

    def test_update_task_duplicate_name(self):
        """
        Ensure that updating the task name to one that already exists for the user returns a 400 error.
        """
        self.client.force_authenticate(user=self.user)
        payload = {
            "name": "Other Task"
        }
        response = self.client.patch(self.detail_url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("already has an object", str(response.data))

    def test_update_task_non_owner(self):
        """
        Ensure that a non-owner is forbidden from updating the task.
        """
        self.client.force_authenticate(user=self.other_user)
        payload = {
            "name": "Updated by non-owner",
            "description": "Should not be allowed"
        }
        response = self.client.patch(self.detail_url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.task.refresh_from_db()
        self.assertEqual(self.task.name, "Test Task")

    def test_update_owner_field_ignored(self):
        """
        Ensure that if the update payload includes a different owner, the original owner remains unchanged.
        """
        self.client.force_authenticate(user=self.user)
        payload = {
            "name": "Updated Task Name",
            "owner": self.other_user.id
        }
        response = self.client.patch(self.detail_url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        # The original owner should remain unchanged.
        self.assertEqual(self.task.owner, self.user)
