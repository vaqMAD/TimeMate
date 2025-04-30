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


class TimeEntriesByTaskListViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='<EMAIL>', password='<PASSWORD>')
        self.other_user = User.objects.create_user(username='otheruser', email='<EMAIL>', password='<PASSWORD>')

        self.task_a = Task.objects.create(name="Alpha", owner=self.user)
        self.task_b = Task.objects.create(name="Bravo", owner=self.user)

        now = timezone.now()
        self.entries1 = [
            TimeEntry.objects.create(
                task=self.task_a, owner=self.user,
                start_time=now - timedelta(hours=i + 1),
                end_time=now - timedelta(hours=i)
            ) for i in range(3)
        ]
        self.entries2 = [
            TimeEntry.objects.create(
                task=self.task_b, owner=self.user,
                start_time=now + timedelta(hours=i),
                end_time=now + timedelta(hours=i + 1)
            ) for i in range(2)
        ]

        self.url = reverse('time_entry_sorted_by_task_name')
        self.client.force_authenticate(user=self.user)

    def test_no_task_returns_empty_list(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'], [])

    def test_task_without_entries(self):
        self.client.force_authenticate(user=self.other_user)
        other_task_a = Task.objects.create(name="Other Alpha", owner=self.other_user)
        other_task_b = Task.objects.create(name="Other Bravo", owner=self.other_user)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([entry['name'] for entry in response.data['results']], [other_task_a.name, other_task_b.name])

    def test_task_entries_structure(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        tasks = response.data['results']
        self.assertEqual(len(tasks), 2)
        response_map = {
            item['id']: [e['id'] for e in item['entries']] for item in tasks
        }
        expected_id_1 = {str(e.id) for e in self.entries1}
        expected_id_2 = {str(e.id) for e in self.entries2}
        self.assertEqual(set(response_map[str(self.task_a.id)]), expected_id_1)
        self.assertEqual(set(response_map[str(self.task_b.id)]), expected_id_2)

    def test_task_with_entries_and_owner_filtering(self):
        self.client.force_authenticate(self.user)

        other_task_a = Task.objects.create(name="Other Alpha", owner=self.other_user)
        other_time_entry_1 = TimeEntry.objects.create(
            task=other_task_a, owner=self.other_user,
            start_time=timezone.now() - timedelta(hours=1),
            end_time=timezone.now()
        )

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        desired_task_names = [self.task_a.name, self.task_b.name]
        received_task_names = [task['name'] for task in response.data['results']]
        self.assertEqual(desired_task_names, received_task_names)
        self.assertNotIn(other_task_a.name, received_task_names)
        for task in response.data['results']:
            self.assertNotIn(other_time_entry_1.id, task['entries'])

    def test_task_entries_count(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_entries_1 = TimeEntry.objects.filter(task=str(self.task_a.id)).count()
        expected_entries_2 = TimeEntry.objects.filter(task=str(self.task_b.id)).count()
        self.assertEqual(len(response.data['results'][0]['entries']), expected_entries_1)
        self.assertEqual(len(response.data['results'][1]['entries']), expected_entries_2)

    def test_ordering_by_task_name(self):
        task_z = Task.objects.create(name="Zeta", owner=self.user)

        response = self.client.get(self.url, {'ordering': 'name'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [task['name'] for task in response.data['results']]
        self.assertEqual(names, [self.task_a.name, self.task_b.name, task_z.name])


class TimeEntriesByDateListViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='<EMAIL>', password='<PASSWORD>')
        self.other_user = User.objects.create_user(username='otheruser', email='<EMAIL>', password='<PASSWORD>')

        self.task_a = Task.objects.create(name="Alpha", owner=self.user)

        now = timezone.now()
        # entry on two days: one yesterday, two today
        self.entry_today_1 = TimeEntry.objects.create(
            task=self.task_a, owner=self.user,
            start_time=now - timedelta(hours=3),
            end_time=now - timedelta(hours=2)
        )
        self.entry_today_2 = TimeEntry.objects.create(
            task=self.task_a, owner=self.user,
            start_time=now - timedelta(hours=5),
            end_time=now - timedelta(hours=4)
        )
        yesterday = now - timedelta(days=1)
        self.entry_yesterday = TimeEntry.objects.create(
            task=self.task_a, owner=self.user,
            start_time=yesterday - timedelta(hours=2),
            end_time=yesterday - timedelta(hours=1)
        )
        # Objects for other user
        self.other_task = Task.objects.create(name="Other", owner=self.other_user)
        self.other_entry = TimeEntry.objects.create(
            owner=self.other_user, task=self.other_task,
            start_time=now - timedelta(days=2, hours=1), end_time=now - timedelta(days=2)
        )

        self.url = reverse('time_entry_sorted_by_date')
        self.client.force_authenticate(user=self.user)

    def test_default_grouping_and_ordering(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['results']

        days = [group['day'] for group in data]
        today_str = timezone.now().date().isoformat()
        yesterday_str = (timezone.now().date() - timedelta(days=1)).isoformat()
        self.assertEqual(days, [today_str, yesterday_str])

        # Check entries within "today" group are ordered by end_time descending
        today_entries = data[0]['entries']
        end_times = [entry['end_time'] for entry in today_entries]
        sorted_end_times = sorted(end_times, reverse=True)
        self.assertEqual(end_times, sorted_end_times)

    def test_ordering_by_day_ascending(self):
        response = self.client.get(self.url, {'ordering': 'day'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['results']

        # Now groups should be [yesterday, today]
        days = [group['day'] for group in data]
        yesterday_str = (timezone.now().date() - timedelta(days=1)).isoformat()
        today_str = timezone.now().date().isoformat()
        self.assertEqual(days, [yesterday_str, today_str])

        # Entries in each group should still be present
        # We don't enforce ordering inside when overriding by day only
        self.assertTrue(all('entries' in group for group in data))

    def test_filtering_by_exact_day(self):
        # filter only yesterday's entries
        today_str = (timezone.now().date()).isoformat()
        response = self.client.get(self.url, {'end_time_before': today_str})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['results']
        self.assertEqual(len(data), 1)
        yesterday_str = (timezone.now().date() - timedelta(days=1)).isoformat()
        self.assertEqual(data[0]['day'], yesterday_str)
        self.assertEqual(len(data[0]['entries']), 1)
        self.assertEqual(data[0]['entries'][0]['id'], str(self.entry_yesterday.id))

    def test_no_entries_returns_empty_results(self):
        new_user = User.objects.create_user(username='newuser', email='<EMAIL>', password='<PASSWORD>')
        self.client.force_authenticate(user=new_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'], [])