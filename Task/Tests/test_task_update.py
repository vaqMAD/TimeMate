# Django imports
from django.urls import reverse
# DRF imports
from rest_framework import status
# Internal imports
from TimeMate.Utils.test_helpers import get_error_code
from Task.models import Task
from Task.validators import VALIDATION_ERROR_CODE_UNIQUE_TASK_NAME
from TimeMate.Permissions.owner_permissions import PERMISSION_ERROR_CODE_NOT_TASK_OWNER
from .base import BaseTaskAPITestCase


class TaskUpdateTests(BaseTaskAPITestCase):
    def setUp(self):

        # Create task instances for testing.
        self.task = Task.objects.create(name="Test Task", owner=self.user1)
        self.other_task = Task.objects.create(name="Other Task", owner=self.user1)

        # Set up the URL for the task detail view.
        self.detail_url = reverse('task_detail', kwargs={'pk': self.task.id})

    def test_update_task_success(self):
        """
        Ensure that the task owner can update the task's name and description.
        """
        self.authenticate(self.user1)
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
        self.authenticate(self.user1)
        payload = {"name": "Other Task"}

        response = self.client.patch(self.detail_url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Błąd walidacji na polu 'name'
        self.assertIn('name', response.data)
        self.assertEqual(
            get_error_code(response.data['name']),
            VALIDATION_ERROR_CODE_UNIQUE_TASK_NAME
        )

    def test_update_task_non_owner(self):
        """
        Ensure that a non-owner is forbidden from updating the task.
        """
        self.authenticate(self.user2)
        payload = {
            "name": "Updated by non-owner",
            "description": "Should not be allowed"
        }

        response = self.client.patch(self.detail_url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('detail', response.data)
        self.assertEqual(
            get_error_code(response.data['detail']),
            PERMISSION_ERROR_CODE_NOT_TASK_OWNER
        )

    def test_update_owner_field_ignored(self):
        """
        Ensure that if the update payload includes a different owner, the original owner remains unchanged.
        """
        self.authenticate(self.user1)
        payload = {
            "name": "Updated Task Name",
            "owner": self.user2.id
        }

        response = self.client.patch(self.detail_url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        # Owner pozostaje user1
        self.assertEqual(self.task.owner, self.user1)
