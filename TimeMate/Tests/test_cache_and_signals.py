# Python imports
from datetime import timedelta
# Django imports
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from django.core.cache import cache
# Drf imports
from rest_framework import status
from rest_framework.test import APITestCase
# Internal imports
from TimeEntry.models import TimeEntry
from Task.models import Task
from TimeMate.Signals.signals import invalidate_user_list

User = get_user_model()


class CacheAndSignalTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='user1', password='<PASSWORD>', email='<EMAIL>')
        self.client.force_authenticate(user=self.user)

        cache.clear()

        self.task = Task.objects.create(name='Test Task', owner=self.user)
        for i in range(3):
            TimeEntry.objects.create(
                task=self.task,
                owner=self.user,
                start_time=timezone.now(),
                end_time=timezone.now() + timedelta(hours=i + 1)
            )
        # URL patterns
        self.time_entry_list_url = reverse('time_entry_list_create')

        self.time_entry_detail_url = lambda pk: reverse('time_entry_detail', args=[pk])
        self.time_entry_by_task_url = reverse('time_entry_sorted_by_task_name')
        self.time_entry_by_date_url = reverse('time_entry_sorted_by_date')
        self.task_list_create_url = reverse('task_list_create')
        self.task_detail_url = lambda pk: reverse('task_detail', args=[pk])

    def test_cache_list_mixin_sets_cache_key(self):
        # Ensure, cache is empty
        self.assertFalse(list(cache.iter_keys('*')))
        # First GET: set cache
        response = self.client.get(self.time_entry_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check a cache key exists
        keys = list(cache.iter_keys('*'))
        self.assertTrue(keys)
        # Key should include user id
        self.assertTrue(any(f'user={self.user.id}' in k for k in keys))

    def test_signal_invalidates_cache_on_task_create(self):
        # Set cache
        self.client.get(self.time_entry_list_url)
        self.assertTrue(list(cache.iter_keys('*')))
        # Create a new Task -> should trigger invalidate_user_list, signal
        data = {
            'name': 'New Task',
            'owner': self.user.id
        }
        self.client.post(self.task_list_create_url, data=data)
        # After POST, cache keys for, user should be removed
        keys_after = list(cache.iter_keys('*'))
        self.assertFalse(keys_after)
        self.assertFalse(any(f'user={self.user.id}' in k for k in keys_after))

    def test_signal_invalidates_cache_on_task_update(self):
        # Set cache
        self.client.get(self.time_entry_list_url)
        self.assertTrue(list(cache.iter_keys('*')))
        # Update existing Task
        self.client.patch(self.task_detail_url(self.task.id), {'name': 'Updated'})
        # Cache should be invalidated
        keys_after = list(cache.iter_keys('*'))
        self.assertFalse(keys_after)
        self.assertFalse(any(f'user={self.user.id}' in k for k in keys_after))

    def test_signal_invalidates_cache_on_task_delete(self):
        # Set cache
        self.client.get(self.time_entry_list_url)
        self.assertTrue(list(cache.iter_keys('*')))
        # Delete existing Task
        self.client.delete(self.task_detail_url(self.task.id))
        # Cache should be invalidated
        keys_after = list(cache.iter_keys('*'))
        self.assertFalse(any(f'user={self.user.id}' in k for k in keys_after))

    def test_signal_invalidates_cache_on_time_entry_change(self):
        # Sets cache
        self.client.get(self.time_entry_list_url)
        self.assertTrue(list(cache.iter_keys('*')))
        # Update existing time entry
        update_url = reverse('time_entry_detail', args=[self.task.time_entries.first().id])
        data = {
            'end_time': self.task.time_entries.first().end_time + timedelta(hours=1)
        }
        self.client.patch(update_url, data=data)
        keys_after = list(cache.iter_keys('*'))
        self.assertFalse(keys_after)
        self.assertFalse(any(f'user={self.user.id}' in k for k in keys_after))

    def test_signal_invalidates_cache_on_time_entry_delete(self):
        # Sets cache
        self.client.get(self.time_entry_list_url)
        self.assertTrue(list(cache.iter_keys('*')))
        # Delete existing TimeEntry
        time_entry_id = self.task.time_entries.first().id
        self.client.delete(self.time_entry_detail_url(time_entry_id))
        # Cache should be invalidated
        keys_after = list(cache.iter_keys('*'))
        self.assertFalse(any(f'user={self.user.id}' in k for k in keys_after))

    #########################################################
    ### Combined flow tests for TimeEntriesByTaskListView ###
    #########################################################
    def test_cache_for_time_entries_by_task_list_view(self):
        # Ensure cache empty
        cache.clear()
        # First GET: populates cache
        resp1 = self.client.get(self.time_entry_by_task_url)
        self.assertEqual(resp1.status_code, status.HTTP_200_OK)
        # Check cache set
        keys = list(cache.iter_keys('*'))
        self.assertTrue(any('TimeEntriesByTaskListView' in k for k in keys))
        # Second GET: should hit cache (no DB queries)
        resp2 = self.client.get(self.time_entry_by_task_url)
        self.assertEqual(resp1.data, resp2.data)

    def test_flow_time_entries_by_task_on_task_create(self):
        cache.clear()
        # initial get and cache
        response_1 = self.client.get(self.time_entry_by_task_url)
        self.assertEqual(response_1.status_code, status.HTTP_200_OK)
        initial_count = len(response_1.data['results'])
        keys = list(cache.iter_keys('*'))
        self.assertTrue(keys)
        self.assertTrue(any(f'user={self.user.id}' in k for k in keys))
        # create tasks
        response_create = self.client.post(self.task_list_create_url, data={'name': 'New Task', 'owner': self.user.id})
        self.assertEqual(response_create.status_code, status.HTTP_201_CREATED)
        # cache invalidated
        keys_after = list(cache.iter_keys('*'))
        self.assertFalse(keys_after)
        self.assertFalse(any(f'user={self.user.id}' in k for k in keys_after))
        # second GET populates new cache and includes new task.
        response_2 = self.client.get(self.time_entry_by_task_url)
        self.assertEqual(response_2.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_2.data['results']), initial_count + 1)
        self.assertTrue(any(item['name'] == 'New Task' for item in response_2.data['results']))

    def test_flow_time_entries_by_task_on_task_update(self):
        cache.clear()
        resp1 = self.client.get(self.time_entry_by_task_url)
        initial_names = {item['name'] for item in resp1.data['results']}
        # update existing Task -> invalidates cache
        upd = self.client.patch(self.task_detail_url(self.task.id), {'name': 'Updated Task'})
        self.assertEqual(upd.status_code, status.HTTP_200_OK)
        self.assertFalse(list(cache.iter_keys('*')))
        # new GET: should include, updated name
        resp2 = self.client.get(self.time_entry_by_task_url)
        names_after = {item['name'] for item in resp2.data['results']}
        self.assertIn('Updated Task', names_after)
        self.assertNotEqual(names_after, initial_names)

    def test_flow_time_entries_by_task_on_task_delete(self):
        cache.clear()
        resp1 = self.client.get(self.time_entry_by_task_url)
        initial_count = len(resp1.data['results'])
        # delete Task -> invalidates cache
        deleted = self.client.delete(self.task_detail_url(self.task.id))
        self.assertEqual(deleted.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(list(cache.iter_keys('*')))
        # new GET: count should decrease
        resp2 = self.client.get(self.time_entry_by_task_url)
        self.assertEqual(len(resp2.data['results']), initial_count - 1)

    def test_flow_time_entries_by_task_on_time_entry_create(self):
        cache.clear()
        # initial get and cache
        response_1 = self.client.get(self.time_entry_by_task_url)
        self.assertEqual(response_1.status_code, status.HTTP_200_OK)
        initial_count = sum(len(item['entries']) for item in response_1.data['results'])
        keys = list(cache.iter_keys('*'))
        self.assertTrue(keys)
        self.assertTrue(any(f'user={self.user.id}' in k for k in keys))
        # create time_entry
        data = {
            'task': str(self.task.id),
            'start_time': timezone.now().isoformat(),
            'end_time': (timezone.now() + timedelta(hours=1)).isoformat(),
        }
        self.client.post(self.time_entry_list_url, data=data)
        # cache invalidated
        keys_after = list(cache.iter_keys('*'))
        self.assertFalse(keys_after)
        self.assertFalse(any(f'user={self.user.id}' in k for k in keys_after))
        response_2 = self.client.get(self.time_entry_by_task_url)
        self.assertEqual(response_2.status_code, status.HTTP_200_OK)
        total_time_entries = sum(len(item['entries']) for item in response_2.data['results'])
        self.assertEqual(total_time_entries, initial_count + 1)

    def test_flow_time_entries_by_task_on_time_entry_update(self):
        cache.clear()
        resp1 = self.client.get(self.time_entry_by_task_url)
        # pick one entry and update -> invalidates cache
        entry_id = resp1.data['results'][0]['entries'][0]['id']
        upd = self.client.patch(self.time_entry_detail_url(entry_id),
                                {'end_time': (timezone.now() + timedelta(hours=5)).isoformat()})
        self.assertEqual(upd.status_code, status.HTTP_200_OK)
        self.assertFalse(list(cache.iter_keys('*')))
        # new GET: verify entry exists and was updated
        resp2 = self.client.get(self.time_entry_by_task_url)
        entries = resp2.data['results'][0]['entries']
        self.assertTrue(any(e['id'] == entry_id for e in entries))

    def test_flow_time_entries_by_task_on_time_entry_delete(self):
        cache.clear()
        resp1 = self.client.get(self.time_entry_by_task_url)
        initial_total = sum(len(item['entries']) for item in resp1.data['results'])
        # delete one entry -> invalidates cache
        entry_id = resp1.data['results'][0]['entries'][0]['id']
        deleted = self.client.delete(self.time_entry_detail_url(entry_id))
        self.assertEqual(deleted.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(list(cache.iter_keys('*')))
        # new GET: total decreases by one
        resp2 = self.client.get(self.time_entry_by_task_url)
        new_total = sum(len(item['entries']) for item in resp2.data['results'])
        self.assertEqual(new_total, initial_total - 1)

    #########################################################
    ### Combined flow tests for TimeEntryByDateListView ###
    #########################################################
    def test_cache_for_time_entry_by_date_list_view(self):
        cache.clear()
        resp1 = self.client.get(self.time_entry_by_date_url)
        self.assertEqual(resp1.status_code, status.HTTP_200_OK)
        keys = list(cache.iter_keys('*'))
        self.assertTrue(any('TimeEntryByDateListView' in k for k in keys))
        resp2 = self.client.get(self.time_entry_by_date_url)
        self.assertEqual(resp1.data, resp2.data)

    def test_flow_time_entry_by_date_on_time_entry_create(self):
        cache.clear()
        # initial GET and cache
        resp1 = self.client.get(self.time_entry_by_date_url)
        self.assertEqual(resp1.status_code, status.HTTP_200_OK)
        initial_count = len(resp1.data['results'])
        # create new time entry -> invalidates cache
        new_entry_data = {
            'task': str(self.task.id),
            'start_time': (timezone.now() + timedelta(days=1)).isoformat(),
            'end_time': (timezone.now() + timedelta(days=1, hours=1)).isoformat(),
        }
        create_resp = self.client.post(self.time_entry_list_url, new_entry_data)
        self.assertEqual(create_resp.status_code, status.HTTP_201_CREATED)
        # cache should be cleared
        self.assertFalse(list(cache.iter_keys('*')))
        # second GET: new cache and count increased
        resp2 = self.client.get(self.time_entry_by_date_url)
        self.assertEqual(len(resp2.data['results']), initial_count + 1)
        # verify new day group present
        new_day = (timezone.now().date() + timedelta(days=1)).isoformat()
        self.assertTrue(any(group['day'] == new_day for group in resp2.data['results']))

    def test_flow_time_entry_by_date_on_time_entry_update(self):
        cache.clear()
        resp1 = self.client.get(self.time_entry_by_date_url)
        # update one entry -> invalidates cache
        entry_id = resp1.data['results'][0]['entries'][0]['id']
        new_end = (timezone.now() + timedelta(days=2)).isoformat()
        upd = self.client.patch(self.time_entry_detail_url(entry_id), {'end_time': new_end})
        self.assertEqual(upd.status_code, status.HTTP_200_OK)
        self.assertFalse(list(cache.iter_keys('*')))
        # new GET: verify updated 'day' field moved group.
        resp2 = self.client.get(self.time_entry_by_date_url)
        days = {group['day'] for group in resp2.data['results']}
        expected_day = (timezone.now().date() + timedelta(days=2)).isoformat()
        self.assertIn(expected_day, days)

    def test_flow_time_entry_by_date_on_time_entry_delete(self):
        cache.clear()
        # initial GET and cache
        resp1 = self.client.get(self.time_entry_by_date_url)
        self.assertEqual(resp1.status_code, status.HTTP_200_OK)
        # count total entries across all days
        total_entries_before = sum(len(group['entries']) for group in resp1.data['results'])
        # delete one entry -> invalidates cache
        entry_id = resp1.data['results'][0]['entries'][0]['id']
        deleted = self.client.delete(self.time_entry_detail_url(entry_id))
        self.assertEqual(deleted.status_code, status.HTTP_204_NO_CONTENT)
        # cache should be cleared
        self.assertFalse(list(cache.iter_keys('*')))
        # new GET: total entries decreased by one
        resp2 = self.client.get(self.time_entry_by_date_url)
        total_entries_after = sum(len(group['entries']) for group in resp2.data['results'])
        self.assertEqual(total_entries_after, total_entries_before - 1)

    def test_flow_time_entry_by_date_on_task_create(self):
        cache.clear()
        resp1 = self.client.get(self.time_entry_by_date_url)
        initial_count = len(resp1.data['results'])
        # create a new task (no new entries) -> invalidates cache
        create = self.client.post(self.task_list_create_url, {'name': 'Another Task'})
        self.assertEqual(create.status_code, status.HTTP_201_CREATED)
        self.assertFalse(list(cache.iter_keys('*')))
        # new GET: count remains, same
        resp2 = self.client.get(self.time_entry_by_date_url)
        self.assertEqual(len(resp2.data['results']), initial_count)

    def test_flow_time_entry_by_date_on_task_update(self):
        cache.clear()
        resp1 = self.client.get(self.time_entry_by_date_url)
        # task names in nested entries
        first_entry = resp1.data['results'][0]['entries'][0]
        old_task_name = first_entry['task']['name']
        # update task
        upd = self.client.patch(self.task_detail_url(self.task.id), {'name': 'Renamed Task'})
        self.assertEqual(upd.status_code, status.HTTP_200_OK)
        self.assertFalse(list(cache.iter_keys('*')))
        # new GET: nested 'task.name' updated
        resp2 = self.client.get(self.time_entry_by_date_url)
        new_name = resp2.data['results'][0]['entries'][0]['task']['name']
        self.assertEqual(new_name, 'Renamed Task')
        self.assertNotEqual(new_name, old_task_name)

    def test_flow_time_entry_by_date_on_task_delete(self):
        cache.clear()
        resp1 = self.client.get(self.time_entry_by_date_url)
        initial_count = len(resp1.data['results'])
        # delete task -> cascades entries deletion
        deleted = self.client.delete(self.task_detail_url(self.task.id))
        self.assertEqual(deleted.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(list(cache.iter_keys('*')))
        # new GET: count decreased by entry count
        resp2 = self.client.get(self.time_entry_by_date_url)
        self.assertTrue(len(resp2.data['results']) < initial_count)

    def test_invalidate_user_list_direct(self):
        # Manually set multiple cache entries
        cache.set(f"a:user={self.user.id}:x", 'foo', 60)
        cache.set(f"b:user={self.user.id}:y", 'bar', 60)
        cache.set(f"c:user=999:z", 'baz', 60)
        # Check count
        all_keys = list(cache.iter_keys('*'))
        self.assertEqual(sum(1 for k in all_keys if f'user={self.user.id}' in k), 2)
        # Invalidate for user
        invalidate_user_list(self.user.id)
        remaining = list(cache.iter_keys('*'))
        self.assertFalse(any(f'user={self.user.id}' in k for k in remaining))
        self.assertTrue(any('user=999' in k for k in remaining))
