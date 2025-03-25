# Python imports
from datetime import timedelta
# Django Imports
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
# DRF Imports
from rest_framework.test import APITestCase
# Internal imports
from TimeEntry.models import TimeEntry
from Task.models import Task

User = get_user_model()

# # TODO [InProgress/NOTE] : This test class is a Work In Progress.
# The existing tests are under active development and are subject to further reviews and refinements.
class TimeEntryListTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='<EMAIL>', password='<PASSWORD>')
        self.task = Task.objects.create(name='Test Task', owner=self.user)
        self.time_entry_sample_object = TimeEntry.objects.create(
            task=self.task,
            owner=self.user,
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(hours=1)
        )
        self.url = reverse('time_entry_list_create')

    def test_list_time_entries(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['task']['id'], str(self.task.id))