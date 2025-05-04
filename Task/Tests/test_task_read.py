# Python imports
from asyncio import create_task
from datetime import timedelta
# Django imports
from django.urls import reverse
from django.utils import timezone
# DRF imports
from rest_framework import status
from rest_framework.test import APITestCase
# Internal imports
from TimeMate.Utils.test_helpers import get_error_code
from Task.models import Task
from TimeMate.Permissions.owner_permissions import PERMISSION_ERROR_CODE_NOT_TASK_OWNER
from .base import BaseTaskAPITestCase, BaseTaskListViewTestCase


class TaskDetailViewTests(BaseTaskAPITestCase):
    """
    Tests for the TaskDetailView.
    This class verifies that the view returns task details for the owner
    and denies access for non-owners.
    """

    def setUp(self):
        # Create a task assigned to the owner.
        self.task = Task.objects.create(name="Test Task", owner=self.user1)

        # Build the URL for TaskDetailView using the task's primary key.
        self.detail_url = reverse('task_detail', kwargs={'pk': self.task.pk})

    def test_task_detail_view_returns_task_for_owner(self):
        """
        Verify that TaskDetailView returns the correct task data for the owner.
        """
        self.authenticate(self.user1)
        response = self.client.get(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], str(self.task.id))
        self.assertEqual(response.data['name'], self.task.name)

    def test_task_detail_view_denies_access_for_non_owner(self):
        """
        Verify that TaskDetailView denies access for a user who is not the task owner.
        """
        # Authenticate as a non-owner.
        self.authenticate(self.user2)
        response = self.client.get(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            get_error_code(response.data['detail']),
            PERMISSION_ERROR_CODE_NOT_TASK_OWNER
        )


class TaskListViewTests(BaseTaskListViewTestCase):
    """
    Tests for the TaskList endpoint without filters.
    """

    def test_task_list_view_returns_task_for_authenticated_user(self):
        """
        Verify that TaskListCreateView returns only the tasks assigned to the authenticated user.
        """
        self.create_task(user=self.user, amount=2)

        self.authenticate_user(self.user)

        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        task_names = [item['name'] for item in response.data['results']]
        task_ids = [item['id'] for item in response.data['results']]
        user_tasks = Task.objects.filter(owner=self.user)
        self.assertEqual(len(response.data['results']), user_tasks.count())
        for task in user_tasks:
            self.assertIn(str(task.name), task_names)
            self.assertIn(str(task.id), task_ids)

    def test_task_list_view_not_returns_task_belonging_to_another_user(self):
        """
        Verify that TaskListCreateView does not return tasks that are not assigned to the authenticated user.
        """
        # Create a task assigned to user.
        self.create_task(user=self.user, amount=2)
        # Create a task assigned to another user.
        other_task = Task.objects.create(name="Other Task", owner=self.other_user)

        self.authenticate_user(self.user)

        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        task_names = [item['name'] for item in response.data['results']]
        task_ids = [item['id'] for item in response.data['results']]

        self.assertNotIn(str(other_task.name), task_names)
        self.assertNotIn(str(other_task.id), task_ids)

    def test_task_list_view_returns_empty_list_for_user_without_tasks(self):
        """
        Verify that TaskListCreateView returns an empty list for a user with no assigned tasks.
        """
        self.client.force_authenticate(user=self.no_task_user)
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Expect, results list to be empty.
        self.assertEqual(len(response.data['results']), 0)


class TaskListViewFilterPaginationTests(BaseTaskListViewTestCase):
    """
    Tests for filtering and pagination in TaskListCreateView.
    This class verifies that pagination works correctly and that the filters
    for 'name' and 'created_at' return the expected results.
    """

    def test_pagination_defaults(self):
        """
        Verify that pagination returns the default page size (10) and the correct total count.
        """
        self.create_task(user=self.user, amount=25)
        self.authenticate_user(self.user)
        user_tasks_count = Task.objects.filter(owner=self.user).count()

        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that there are 10 tasks in results (default page size).
        self.assertEqual(len(response.data['results']), 10)
        # Verify the total count of tasks for the user.
        self.assertEqual(response.data['count'], user_tasks_count)
        # Ensure pagination links are present.
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)

    def test_no_results_when_filter_criteria_not_match(self):
        """
        Verify that no results are returned when the filter criteria does not match any task.
        """
        self.authenticate_user(self.user)
        response = self.client.get(self.list_url, {'name': 'non-existent-task'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data['results']), 0)
        self.assertEqual(response.data['count'], 0)

    def test_view_filter_by_task_name_does_not_return_entries_not_owned_by_user(self):
        """
        Ensure that filtering by task name does not return entries that are not owned by the user.
        """
        self.authenticate_user(self.user)
        task_owned_by_other_user = Task.objects.create(name="Unique Name", owner=self.other_user)
        response = self.client.get(self.list_url, {'name': str(task_owned_by_other_user.name)})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data['results']), 0)
        self.assertEqual(response.data['count'], 0)

    def test_filter_by_name(self):
        """
        Verify that filtering by task name returns only tasks whose name contains the specified substring.
        """
        alpha = Task.objects.create(name="Alpha", owner=self.user)
        beta = Task.objects.create(name="Beta Task", owner=self.user)
        alpha_another = Task.objects.create(name="Alpha Another", owner=self.user)
        self.authenticate_user(self.user)

        # Create a task with a unique name for filtering.
        data = {'name': alpha.name}
        # Send a GET request with the 'name' filter parameter.
        response = self.client.get(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        task_names = [item['name'] for item in response.data['results']]
        self.assertIn(str(alpha.name), task_names)
        self.assertIn(str(alpha_another.name), task_names)
        self.assertNotIn(beta.name, task_names)

    def test_filter_by_created_at_range(self):
        """
        Verify that filtering by a range of 'created_at' dates (using both 'created_at_after' and 'created_at_before')
        returns the expected number of tasks.
        """
        today_tasks = self.create_task(user=self.user, amount=15)

        # Create an excluded task with an older 'created_at' timestamp.
        excluded_task = Task.objects.create(name="Excluded Task", owner=self.user)
        excluded_task.created_at = timezone.now() - timedelta(days=2)
        excluded_task.save()

        data = {
            "created_at_after": timezone.now() - timedelta(days=1),
            "created_at_before": timezone.now() + timedelta(days=1)
        }
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Since all tasks created in, first line of test are within the last day, there should be 15 tasks in total.
        self.assertEqual(response.data['count'], len(today_tasks))
        # Ensure the excluded task (created more than a day ago) is not in the returned results.
        results = response.data['results']
        found = any(task['id'] == str(excluded_task.id) for task in results)
        self.assertFalse(found)

    def test_filter_by_created_at_after(self):
        """
        Verify that filtering by 'created_at_after' returns only tasks created after the specified cutoff date.
        """
        # Create two tasks and manually adjust their 'created_at' timestamps.
        old, new = self.create_task(self.user, amount=2)
        # Update timestamps: task_old is older; task_new is newer.
        Task.objects.filter(pk=old.pk).update(created_at=timezone.now() - timedelta(days=2))
        Task.objects.filter(pk=new.pk).update(created_at=timezone.now() - timedelta(days=1))
        self.authenticate_user(self.user)

        # Define the cutoff date: tasks created after this date should be returned.
        cutoff = timezone.now() - timedelta(days=1)
        data = {"created_at_after": cutoff.date()}
        response = self.client.get(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Get the list of returned task IDs.
        returned_ids = {t["id"] for t in response.data.get("results", [])}
        self.assertIn(str(new.id), returned_ids)
        self.assertNotIn(str(old.id), returned_ids)

    def test_filter_by_created_at_before(self):
        """
        Verify that filtering by 'created_at_before' returns only tasks created before the specified cutoff date.
        """
        old, new = self.create_task(self.user, amount=2)
        Task.objects.filter(pk=old.pk).update(created_at=timezone.now() - timedelta(days=2))
        Task.objects.filter(pk=new.pk).update(created_at=timezone.now() - timedelta(days=1))

        self.authenticate_user(self.user)

        cutoff = timezone.now() - timedelta(days=1)
        data = {"created_at_before": cutoff.date()}
        response = self.client.get(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        returned_ids = {t["id"] for t in response.data.get("results", [])}
        self.assertIn(str(old.id), returned_ids)
        self.assertNotIn(str(new.id), returned_ids)