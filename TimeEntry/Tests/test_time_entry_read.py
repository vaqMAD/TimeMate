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


class TimeEntryListTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='<EMAIL>', password='<PASSWORD>')
        self.other_user = User.objects.create_user(username='otheruser', email='<EMAIL>', password='<PASSWORD>')
        self.no_data_user = User.objects.create_user(username='no_time_entries_user', email='<EMAIL>',
                                                     password='<PASSWORD>')
        self.task = Task.objects.create(name='Test Task', owner=self.user)
        self.url = reverse('time_entry_list_create')

        self.time_entries = []
        self.tasks = []
        for i in range(5):
            task = Task.objects.create(name=f'Task {i}', owner=self.user)
            self.tasks.append(task)
            self.time_entries.append(
                TimeEntry.objects.create(
                    task=task,
                    owner=self.user,
                    start_time=timezone.now() - timedelta(hours=2 + i),
                    end_time=timezone.now() - timedelta(hours=1 + i)
                )
            )
        # Objects for different user which should not be returned
        self.other_task = Task.objects.create(name='Other Task', owner=self.other_user)
        self.other_time_entry = TimeEntry.objects.create(task=self.other_task, owner=self.other_user,
                                                         start_time=timezone.now(),
                                                         end_time=timezone.now() + timedelta(hours=1))

    def test_list_time_entries_returns_only_user_entries(self):
        """
        Ensure that the list of time entries returned only contains entries for the current user.
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 5)

        returned_task_ids = {entry['id'] for entry in response.data['results']}
        for time_entry in self.time_entries:
            self.assertIn(str(time_entry.id), returned_task_ids)

        for entry in response.data['results']:
            self.assertIn('task', entry)
            self.assertIn('start_time', entry)
            self.assertIn('end_time', entry)

    def test_list_time_entries_not_returns_objects_belonging_to_another_user(self):
        """
        Verify that view does not return time_entries that are not assigned to the current user.
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 5)
        returned_ids = {entry['id'] for entry in response.data['results']}
        self.assertNotIn(str(self.other_time_entry.id), returned_ids)

    def test_list_time_entries_returns_empty_list_for_user_without_tasks(self):
        """
        Verify that view returns an empty list for a user with no assigned tasks.
        """
        self.client.force_authenticate(user=self.no_data_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 0)
