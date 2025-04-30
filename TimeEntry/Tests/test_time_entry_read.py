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
from TimeMate.Utils.utils import get_error_code
from TimeMate.Permissions.owner_permissions import PERMISSION_ERROR_CODE_NOT_TASK_OWNER
from TimeEntry.models import TimeEntry
from Task.models import Task

User = get_user_model()


class TimeEntryDetailViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='<EMAIL>', password='<PASSWORD>')
        self.other_user = User.objects.create_user(username='otheruser', email='<EMAIL>', password='<PASSWORD>')

        self.user_task = Task.objects.create(name='Test Task', owner=self.user)
        self.user_time_entry = TimeEntry.objects.create(
            task=self.user_task,
            owner=self.user,
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(hours=1)
        )

        self.url = reverse('time_entry_detail', kwargs={'pk': str(self.user_time_entry.id)})

    def test_get_time_entry_by_id(self):
        """
        Verify that DetailView returns the correct task data for the owner.
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], str(self.user_time_entry.id))

    def test_time_entry_view_denies_access_for_non_owner(self):
        """
        Verify that DetailView denies access for a user who is not the task owner.
        """
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        error_detail = response.data['detail']
        self.assertEqual(get_error_code(error_detail), PERMISSION_ERROR_CODE_NOT_TASK_OWNER)


class TimeEntryListViewTests(APITestCase):
    """
    Basic tests for TimeEntry list endpoint without filters.
    """

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='<EMAIL>', password='<PASSWORD>')
        self.other_user = User.objects.create_user(username='otheruser', email='<EMAIL>', password='<PASSWORD>')
        self.no_data_user = User.objects.create_user(username='no_time_entries_user', email='<EMAIL>',
                                                     password='<PASSWORD>')
        self.task = Task.objects.create(name='Test Task', owner=self.user)
        self.url = reverse('time_entry_list_create')

        # Create tasks and time entries for self.user
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
        # Verify each created entry is returned
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

    def test_list_time_entries_returns_empty_list_for_user_without_entries(self):
        """
        Verify that view returns an empty list for a user with no assigned tasks.
        """
        self.client.force_authenticate(user=self.no_data_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)


class TimeEntryListViewFilterPaginationTests(APITestCase):
    """
    Tests for TimeEntry list endpoint with filtering and pagination.
    """

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='<EMAIL>', password='<PASSWORD>')
        self.other_user = User.objects.create_user(username='otheruser', email='<EMAIL>', password='<PASSWORD>')

        # Two distinct tasks for filtering by task name
        self.task1 = Task.objects.create(name="Task 1", owner=self.user)
        self.task2 = Task.objects.create(name="Task 2", owner=self.user)

        # Two entries with specific start and end for range tests
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

        # Additional entries
        for i in range(5):
            TimeEntry.objects.create(
                task=self.task1,
                owner=self.user,
                start_time=timezone.now() - timedelta(days=i, hours=3),
                end_time=timezone.now() - timedelta(days=i, hours=2)
            )

        # Entry belonging to another user should be excluded
        self.task_owned_by_other_user = Task.objects.create(name="Other Task", owner=self.other_user)
        self.time_entry_owned_by_other_user = TimeEntry.objects.create(
            task=self.task_owned_by_other_user,
            owner=self.other_user,
            start_time=timezone.now() - timedelta(hours=3),
            end_time=timezone.now() - timedelta(hours=2)
        )

        self.list_url = reverse('time_entry_list_create')

    def test_pagination_links_present(self):
        """
        Verify that pagination fields 'next' and 'previous' are in the response.
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Ensure pagination links are present.
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)

    def test_filter_start_time_after(self):
        """
        Test filtering entries with start_time greater than or equal to given value.
        """
        self.client.force_authenticate(user=self.user)
        start_date = self.time_entry1.start_time
        data = {'start_time_after': start_date.isoformat()}
        expected_count = TimeEntry.objects.filter(owner=self.user, start_time__gte=data['start_time_after']).count()
        response = self.client.get(self.list_url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), expected_count)

    def test_filter_start_time_before(self):
        """
        Test filtering entries with start_time less than or equal to given value.
        """
        self.client.force_authenticate(user=self.user)
        start_date = self.time_entry1.start_time
        data = {'start_time_before': start_date.isoformat()}
        response = self.client.get(self.list_url, data)
        expected_count = TimeEntry.objects.filter(owner=self.user, start_time__lte=data['start_time_before']).count()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), expected_count)

    def test_filter_end_time_after(self):
        """
        Test filtering entries with end_time greater than or equal to given value.
        """
        self.client.force_authenticate(user=self.user)
        end_date = self.time_entry1.end_time
        data = {'end_time_after': end_date.isoformat()}
        response = self.client.get(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_count = TimeEntry.objects.filter(owner=self.user, end_time__gte=data['end_time_after']).count()
        self.assertEqual(len(response.data['results']), expected_count)

    def test_filter_end_time_before(self):
        """
        Test filtering entries with end_time less than or equal to given value.
        """
        self.client.force_authenticate(user=self.user)
        end_date = self.time_entry1.end_time
        data = {'end_time_before': end_date.isoformat()}
        response = self.client.get(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_count = TimeEntry.objects.filter(owner=self.user, end_time__lte=data['end_time_before']).count()
        self.assertEqual(len(response.data['results']), expected_count)

    def test_list_time_entries_without_filters(self):
        """
         ,
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        user_time_entries_count = TimeEntry.objects.filter(owner=self.user).count()
        self.assertEqual(len(response.data['results']), user_time_entries_count)

    def test_no_results_when_filter_criteria_not_match(self):
        """
        Verify that invalid filter criteria return an empty result set.
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url, {'task': 'Not existing task'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)

    def test_filter_time_entries_by_task(self):
        """
        Verify filtering by task name returns only entries matching the task.
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url, {'task': str(self.task2.name)})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['task']['id'], str(self.task2.id))
        self.assertEqual(response.data['results'][0]['task']['name'], str(self.task2.name))

    def test_view_filter_by_task_does_not_return_time_entries_not_owned_by_user(self):
        """
        Ensure filtering by task name does not expose other users' entries.
        """
        self.client.force_authenticate(user=self.user)
        # Use other user's task name in filter
        response = self.client.get(self.list_url, {'task': str(self.task_owned_by_other_user.name)})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Expect zero results since task belongs to another user
        self.assertEqual(len(response.data['results']), 0)

    def test_view_filter_by_date_time_range_does_not_return_time_entries_not_owned_by_user(self):
        """
        Ensure date range filters exclude entries not owned by the current user.
        """
        self.client.force_authenticate(user=self.user)
        # Define a range that includes self.user entries and other_user entry
        start_date = self.time_entry1.start_time
        end_date = self.time_entry2.end_time + timedelta(minutes=1)
        data = {
            'start_time_after': start_date.strftime('%Y-%m-%dT%H%M'),
            'end_time_before': end_date.strftime('%Y-%m-%dT%H%M')
        }

        response = self.client.get(self.list_url, data)
        # Compute expected count via ORM using same bounds
        user_time_entries_in_range = TimeEntry.objects.filter(
            owner=self.user,
            start_time__gte=self.time_entry1.start_time.isoformat(),
            end_time__lte=self.time_entry2.end_time.isoformat())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Compare API result length to ORM count
        self.assertEqual(len(response.data['results']), user_time_entries_in_range.count())
        self.assertNotIn(self.time_entry_owned_by_other_user, response.data['results'])

    def test_ordering_time_entries_by_start_time(self):
        """
        Ensure that ordering by start_time works as expected.
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url, {'ordering': 'start_time'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        start_times = [entry['start_time'] for entry in results]
        self.assertEqual(start_times, sorted(start_times))

    def test_filter_time_entries_by_date_range(self):
        """
        Test combined date-only filters: start_time_after and start_time_before using 'YYYY-MM-DD'.
        """
        self.client.force_authenticate(user=self.user)

        start_date = timezone.now() - timedelta(days=2)
        end_date = timezone.now() - timedelta(days=1)

        response = self.client.get(self.list_url, {
            'start_time_after': start_date.strftime('%Y-%m-%d'),
            'start_time_before': end_date.strftime('%Y-%m-%d')}
                                   )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Only one entry falls within the date range
        self.assertEqual(len(response.data['results']), 1)


class TimeEntryListViewOrderingTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='<EMAIL>', password='<PASSWORD>')
        self.other_user = User.objects.create_user(username='otheruser', email='<EMAIL>', password='<PASSWORD>')

        self.task_a = Task.objects.create(name="Alpha", owner=self.user)
        self.task_b = Task.objects.create(name="Bravo", owner=self.user)
        self.task_c = Task.objects.create(name="Charlie", owner=self.user)

        now = timezone.now()
        self.e1 = TimeEntry.objects.create(
            task=self.task_a,
            owner=self.user,
            start_time=now,
            end_time=now + timedelta(hours=1)
        )
        self.e2 = TimeEntry.objects.create(
            task=self.task_b,
            owner=self.user,
            start_time=now - timedelta(hours=2),
            end_time=now - timedelta(hours=1)
        )
        self.e3 = TimeEntry.objects.create(
            task=self.task_c,
            owner=self.user,
            start_time=now - timedelta(hours=1),
            end_time=now + timedelta(minutes=30)
        )
        self.url = reverse('time_entry_list_create')
        self.client.force_authenticate(user=self.user)

    def _get_ids(self, ordering_param):
        data = {
            'ordering': ordering_param
        }
        response = self.client.get(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return [entry['id'] for entry in response.data['results']]

    def test_ordering_by_task_name_asc(self):
        ids = self._get_ids('task__name')
        # 'Alpha' < 'Beta' < 'Charlie'
        self.assertEqual(ids, [str(self.e1.id), str(self.e2.id), str(self.e3.id)])

    def test_ordering_by_task_name_desc(self):
        ids = self._get_ids("-task__name")
        self.assertEqual(ids, [str(self.e3.id), str(self.e2.id), str(self.e1.id)])

    def test_ordering_by_start_time_asc(self):
        ids = self._get_ids('start_time')
        self.assertEqual(ids, [str(self.e2.id), str(self.e3.id), str(self.e1.id)])

    def test_ordering_by_start_time_desc(self):
        ids = self._get_ids("-start_time")
        self.assertEqual(ids, [str(self.e1.id), str(self.e3.id), str(self.e2.id)])

    def test_ordering_by_end_time_asc(self):
        ids = self._get_ids("end_time")
        self.assertEqual(ids, [str(self.e2.id), str(self.e3.id), str(self.e1.id)])

    def test_ordering_by_end_time_desc(self):
        ids = self._get_ids("-end_time")
        self.assertEqual(ids, [str(self.e1.id), str(self.e3.id), str(self.e2.id)])

    def test_ordering_by_duration_asc(self):
        ids = self._get_ids('duration')
        # duration to end_time - start_time
        expected = sorted([self.e1, self.e2, self.e3],
                          key=lambda e: (e.end_time - e.start_time))
        self.assertEqual(ids, [str(e.id) for e in expected])


    def test_ordering_by_duration_desc(self):
        ids = self._get_ids('-duration')
        expected = sorted([self.e1, self.e2, self.e3],
                          key=lambda e: (e.end_time - e.start_time),
                          reverse=True)
        self.assertEqual(ids, [str(e.id) for e in expected])