# Django imports
from django.urls import reverse
# DRF imports
from rest_framework import status
# Internal imports
from TimeMate.Utils.test_helpers import get_error_code
from Task.models import Task
from TimeMate.Permissions.owner_permissions import PERMISSION_ERROR_CODE_NOT_TASK_OWNER
from .base import BaseTaskAPITestCase


class TaskDeleteTestCase(BaseTaskAPITestCase):
    def setUp(self):
        self.task = Task.objects.create(name="Test Task", owner=self.user1)
        self.detail_url = reverse('task_detail', kwargs={'pk': self.task.id})

    def test_delete_task_by_owner(self):
        """
        Ensure that the task owner can delete the task.
        """
        self.authenticate(self.user1)
        response = self.client.delete(self.detail_url, kwargs={'pk': self.task.id})
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Task.objects.filter(id=self.task.id).exists())

    def test_delete_task_by_non_owner(self):
        """
        Ensure that a non-owner is forbidden from deleting the task.
        """
        self.authenticate(self.user2)
        response = self.client.delete(self.detail_url, kwargs={'pk': self.task.id})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Task.objects.filter(id=self.task.id).exists())
        self.assertEqual(
            get_error_code(response.data['detail']),
            PERMISSION_ERROR_CODE_NOT_TASK_OWNER
        )
