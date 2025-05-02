# Python imports
import uuid
# Django imports
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
# Drf imports
from rest_framework import status
from rest_framework.test import APITestCase
# Internal imports
from TimeMate.Utils.test_helpers import get_error_code
from TimeMate.Permissions.owner_permissions import PERMISSION_ERROR_CODE_NOT_TASK_OWNER
from TimeEntry.models import TimeEntry
from Task.models import Task

User = get_user_model()


class TimeEntryDeleteTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='<EMAIL>', password='<PASSWORD>')
        self.other_user = User.objects.create_user(username='otheruser', email='<EMAIL>', password='<PASSWORD>')

        self.task = Task.objects.create(name="Test Task", owner=self.user)
        self.time_entry = TimeEntry.objects.create(
            task=self.task,
            owner=self.user,
            start_time=timezone.now(),
            end_time=timezone.now() + timezone.timedelta(hours=1)
        )

        self.other_task = Task.objects.create(name="Other Task", owner=self.other_user)
        self.other_time_entry = TimeEntry.objects.create(
            task=self.other_task,
            owner=self.user,
            start_time=timezone.now(),
            end_time=timezone.now() + timezone.timedelta(hours=1)
        )
        self.detail_url = reverse('time_entry_detail', kwargs={'pk': self.time_entry.id})
        self.other_detail_url = reverse('time_entry_detail', kwargs={'pk': self.other_time_entry.id})

    def test_delete_time_entry_success(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(TimeEntry.DoesNotExist):
            TimeEntry.objects.get(id=self.time_entry.id)

    def test_delete_time_entry_non_owner(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.delete(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        error_detail = response.data['detail']
        self.assertEqual(get_error_code(error_detail), PERMISSION_ERROR_CODE_NOT_TASK_OWNER)

        self.assertTrue(TimeEntry.objects.filter(id=self.time_entry.id).exists())

    def test_delete_time_entry_not_found(self):
        self.client.force_authenticate(user=self.user)
        not_existed_url = reverse('time_entry_detail', kwargs={'pk': uuid.uuid4()})
        response = self.client.delete(not_existed_url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
