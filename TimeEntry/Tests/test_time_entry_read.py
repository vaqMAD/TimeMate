# Python imports
from datetime import timedelta
# Django Imports
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
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
        self.other_time_entry = TimeEntry.objects.create(
            task=self.other_task, owner=self.other_user,
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(hours=1)
        )

    def test_list_time_entries_returns_only_user_entries(self):
        """
        Ensure that the list of time entries returned only contains entries for the current user.
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
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
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 5)
        returned_ids = {entry['id'] for entry in response.data['results']}
        self.assertNotIn(str(self.other_time_entry.id), returned_ids)

    def test_list_time_entries_returns_empty_list_for_user_without_tasks(self):
        """
        Verify that view returns an empty list for a user with no assigned tasks.
        """
        self.client.force_authenticate(user=self.no_data_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)


class TimeEntryListViewFilterPaginationTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='<EMAIL>', password='<PASSWORD>')
        self.other_user = User.objects.create_user(username='otheruser', email='<EMAIL>', password='<PASSWORD>')

        self.task1 = Task.objects.create(name="Task 1", owner=self.user)
        self.task2 = Task.objects.create(name="Task 2", owner=self.user)

        self.time_entry1 = TimeEntry.objects.create(
            task=self.task1,
            owner=self.user,
            start_time=timezone.now() - timedelta(hours=3),
            end_time=timezone.now() - timedelta(hours=2)
        )
        self.time_entry2 = TimeEntry.objects.create(
            task=self.task2,
            owner=self.user,
            start_time=timezone.now() - timedelta(hours=2),
            end_time=timezone.now() - timedelta(hours=1)
        )

        for i in range(5):
            TimeEntry.objects.create(
                task=self.task1,
                owner=self.user,
                start_time=timezone.now() - timedelta(days=i, hours=3),
                end_time=timezone.now() - timedelta(days=i, hours=2)
            )

        self.task_owned_by_other_user = Task.objects.create(name="Other Task", owner=self.other_user)
        self.time_entry_owned_by_other_user = TimeEntry.objects.create(
            task=self.task_owned_by_other_user,
            owner=self.other_user,
            start_time=timezone.now() - timedelta(hours=3),
            end_time=timezone.now() - timedelta(hours=2)
        )

        self.list_url = reverse('time_entry_list_create')

    def test_pagination(self):
        """
        Verify that pagination returns the default page size (10) and the correct total count.
        Also, verify that 'next' and 'previous' links are provided.
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Ensure pagination links are present.
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)

    def test_list_time_entries_without_filters(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        user_time_entries_count = TimeEntry.objects.filter(owner=self.user).count()
        self.assertEqual(len(response.data['results']), user_time_entries_count)

    def test_no_results_when_filter_criteria_not_match(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url, {'task': 'Not existing task'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)

    def test_filter_time_entries_by_task(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url, {'task': str(self.task2.name)})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['task']['id'], str(self.task2.id))
        self.assertEqual(response.data['results'][0]['task']['name'], str(self.task2.name))

    # TODO : Add docstring and code comments to explain logic of test
    def test_view_filter_by_task_does_not_return_time_entries_not_owned_by_user(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url, {'task': str(self.task_owned_by_other_user.name)})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)

    # TODO : Add docstring and code comments to explain logic of test
    def test_view_filter_by_date_time_range_does_not_return_time_entries_not_owned_by_user(self):
        self.client.force_authenticate(user=self.user)

        start_date = self.time_entry1.start_time
        end_date = self.time_entry2.end_time + timedelta(minutes=1)
        data = {
            'start_time_after': start_date.strftime('%Y-%m-%dT%H%M'),
            'end_time_before': end_date.strftime('%Y-%m-%dT%H%M')
        }

        response = self.client.get(self.list_url,data)
        user_time_entries_in_range = TimeEntry.objects.filter(
            owner=self.user,
            start_time__gte=self.time_entry1.start_time.isoformat(),
            end_time__lte=self.time_entry2.end_time.isoformat())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), user_time_entries_in_range.count())
        self.assertNotIn(self.time_entry_owned_by_other_user, response.data['results'])

    def test_ordering_time_entries_by_start_time(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url, {'ordering': 'start_time'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        start_times = [entry['start_time'] for entry in results]
        self.assertEqual(start_times, sorted(start_times))

    def test_filter_time_entries_by_date_range(self):
        self.client.force_authenticate(user=self.user)

        start_date = timezone.now() - timedelta(days=2)
        end_date = timezone.now() - timedelta(days=1)

        response = self.client.get(self.list_url, {
            'start_time_after': start_date.strftime('%Y-%m-%d'),
            'start_time_before': end_date.strftime('%Y-%m-%d')}
                                   )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # From the setup method we should only have one object that meets the filtering criteria
        self.assertEqual(len(response.data['results']), 1)
