# tests/test_task_delete.py
# Django imports
from django.urls import reverse
from django.contrib.auth import get_user_model
# DRF imports
from rest_framework import status
from rest_framework.test import APITestCase
# Internal imports
from Task.models import Task
from TimeMate.Permissions.owner_permissions import PERMISSION_ERROR_CODE_NOT_TASK_OWNER

User = get_user_model()


class TaskDeleteTestCase(APITestCase):
    def setUp(self):
        # Set up user objects for testing.
        self.user = User.objects.create_user(username='user1', password='<PASSWORD>', email='<EMAIL>')
        self.other_user = User.objects.create_user(username='user2', password='<PASSWORD>', email='<EMAIL>')

        # Create a task instance for testing.
        self.task = Task.objects.create(name="Test Task", owner=self.user)

        # Set up the URL for the task detail view.
        self.detail_url = reverse('task_detail', kwargs={'pk': self.task.id})

    def test_delete_task_by_owner(self):
        """
        Ensure that the task owner can delete the task.
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Task.objects.filter(id=self.task.id).exists())

    def test_delete_task_by_non_owner(self):
        """
        Ensure that a non-owner is forbidden from deleting the task.
        """
        self.client.force_authenticate(user=self.other_user)
        response = self.client.delete(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Task.objects.filter(id=self.task.id).exists())
        detail = response.data.get("detail")
        self.assertEqual(detail.code, PERMISSION_ERROR_CODE_NOT_TASK_OWNER)
