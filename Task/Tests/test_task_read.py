# Python imports
from datetime import timedelta
# Django imports
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
# DRF imports
from rest_framework import status
from rest_framework.test import APITestCase
# Internal imports
from Task.models import Task
from TimeMate.Permissions.owner_permissions import PERMISSION_ERROR_CODE_NOT_TASK_OWNER

User = get_user_model()


class TaskDetailViewTests(APITestCase):
    """
    Tests for the TaskDetailView.
    This class verifies that the view returns task details for the owner
    and denies access for non-owners.
    """

    def setUp(self):
        # Set up user objects for testing.
        self.user_owner = User.objects.create_user(
            username='user1', password='<PASSWORD>', email='<EMAIL>'
        )
        self.user_not_owner = User.objects.create_user(
            username='user2', password='<PASSWORD>', email='<EMAIL>'
        )

        # Create a task assigned to the owner.
        self.task = Task.objects.create(name="Test Task", owner=self.user_owner)

        # Build the URL for TaskDetailView using the task's primary key.
        self.detail_url = reverse('task_detail', kwargs={'pk': self.task.pk})

    def test_task_detail_view_returns_task_for_owner(self):
        """
        Verify that TaskDetailView returns the correct task data for the owner.
        """
        # Authenticate as the task owner.
        self.client.force_authenticate(user=self.user_owner)
        # Send a GET request to the detail URL.
        response = self.client.get(self.detail_url)

        # Check that the response is OK and the task details match.
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], str(self.task.id))
        self.assertEqual(response.data['name'], self.task.name)

    def test_task_detail_view_denies_access_for_non_owner(self):
        """
        Verify that TaskDetailView denies access for a user who is not the task owner.
        """
        # Authenticate as a non-owner.
        self.client.force_authenticate(user=self.user_not_owner)
        # Send a GET request to the detail URL.
        response = self.client.get(self.detail_url)

        # Expect a 403 Forbidden response.
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        error_detail = response.data.get("detail")
        self.assertEqual(error_detail.code, PERMISSION_ERROR_CODE_NOT_TASK_OWNER)


class TaskListViewTests(APITestCase):
    """
    Tests for the TaskListView.
    This class checks that the view returns only tasks assigned to the authenticated user.
    """

    def setUp(self):
        # Create test users.
        self.user = User.objects.create_user(
            username='user1', password='<PASSWORD>', email='<EMAIL>'
        )
        self.other_user = User.objects.create_user(
            username='user2', password='<PASSWORD>', email='<EMAIL>'
        )
        self.no_task_user = User.objects.create_user(
            username='user3', password='<PASSWORD>', email='<EMAIL>'
        )

        # Create tasks for the authenticated user.
        self.task1 = Task.objects.create(name="Task 1", owner=self.user)
        self.task2 = Task.objects.create(name="Task 2", owner=self.user)
        # Create a task for another user, which should not appear in the results.
        self.task3 = Task.objects.create(name="Task 3", owner=self.other_user)

        # Set up the URL for TaskListView.
        self.list_url = reverse("task_list")

    def test_task_list_view_returns_task_for_authenticated_user(self):
        """
        Verify that TaskListView returns only the tasks assigned to the authenticated user.
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check that the results list contains exactly two tasks.
        self.assertEqual(len(response.data['results']), 2)
        # Create a set of task IDs from the results.
        returned_ids = {task['id'] for task in response.data['results']}
        # Verify that the tasks created for this user are present.
        self.assertIn(str(self.task1.id), returned_ids)
        self.assertIn(str(self.task2.id), returned_ids)

    def test_task_list_view_not_returns_task_belonging_to_another_user(self):
        """
        Verify that TaskListView does not return tasks that are not assigned to the authenticated user.
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check that only two tasks are returned in results.
        self.assertEqual(len(response.data['results']), 2)
        returned_ids = {task['id'] for task in response.data['results']}
        # Verify that the task belonging to another user is not included.
        self.assertNotIn(str(self.task3.id), returned_ids)

    def test_task_list_view_returns_empty_list_for_user_without_tasks(self):
        """
        Verify that TaskListView returns an empty list for a user with no assigned tasks.
        """
        self.client.force_authenticate(user=self.no_task_user)
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Expect results list to be empty.
        self.assertEqual(len(response.data['results']), 0)


class TaskListViewFilterPaginationTests(APITestCase):
    """
    Tests for filtering and pagination in TaskListView.
    This class verifies that pagination works correctly and that the filters
    for 'name' and 'created_at' return the expected results.
    """

    def setUp(self):
        # Create test users.
        self.user = User.objects.create_user(
            username='user1', password='<PASSWORD>', email='<EMAIL>'
        )

        # Create 15 Task objects for the authenticated user.
        for i in range(15):
            Task.objects.create(name=f"Task {i}", owner=self.user)

        # Set up the URL for TaskListView.
        self.list_url = reverse("task_list")

    def test_pagination(self):
        """
        Verify that pagination returns the default page size (10) and the correct total count.
        Also, verify that 'next' and 'previous' links are provided.
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check that there are 10 tasks in results (default page size).
        self.assertEqual(len(response.data['results']), 10)
        # Verify the total count of tasks for the user is 15.
        self.assertEqual(response.data['count'], 15)
        # Ensure pagination links are present.
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)

    def test_filter_by_name(self):
        """
        Verify that filtering by task name returns only tasks whose name contains the specified substring.
        """
        self.client.force_authenticate(user=self.user)
        # Create a task with a unique name for filtering.
        unique_task = Task.objects.create(name="Unique Test Task", owner=self.user)
        # Send a GET request with the 'name' filter parameter.
        response = self.client.get(self.list_url + "?name=Unique Test")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Extract the list of tasks from the paginated results.
        results = response.data['results']
        # Check if any task in the results matches the unique task's ID.
        found = any(task['id'] == str(unique_task.id) for task in results)
        self.assertTrue(found)

    def test_filter_by_created_at_range(self):
        """
        Verify that filtering by a range of 'created_at' dates (using both 'created_at_after' and 'created_at_before')
        returns the expected number of tasks.
        """
        self.client.force_authenticate(user=self.user)
        now = timezone.now()
        yesterday = now - timedelta(days=1)
        tomorrow = now + timedelta(days=1)
        # Build a URL with date filters using date only.
        url_with_date = (
            f"{self.list_url}?created_at_after={yesterday.date()}&created_at_before={tomorrow.date()}"
        )
        response = self.client.get(url_with_date)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Since all tasks created in setUp fall within this date range, the count should be 15.
        self.assertEqual(response.data['count'], 15)

    def test_filter_by_created_at_after(self):
        """
        Verify that filtering by 'created_at_after' returns only tasks created after the specified cutoff date.
        """
        self.client.force_authenticate(user=self.user)
        now = timezone.now()

        # Create two tasks and manually adjust their 'created_at' timestamps.
        task_old = Task.objects.create(name="Old Task", owner=self.user)
        task_new = Task.objects.create(name="New Task", owner=self.user)
        # Update timestamps: task_old is older; task_new is newer.
        Task.objects.filter(pk=task_old.pk).update(created_at=now - timedelta(days=2))
        Task.objects.filter(pk=task_new.pk).update(created_at=now - timedelta(days=1))

        # Define the cutoff date: tasks created after this date should be returned.
        cutoff = now - timedelta(days=1)
        url_with_after = f"{self.list_url}?created_at_after={cutoff.date()}"
        response = self.client.get(url_with_after)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Get the list of returned task IDs.
        results = response.data.get("results", [])
        returned_ids = [t["id"] for t in results]
        # Verify that only the newer task is returned.
        self.assertIn(str(task_new.id), returned_ids)
        self.assertNotIn(str(task_old.id), returned_ids)

    def test_filter_by_created_at_before(self):
        """
        Verify that filtering by 'created_at_before' returns only tasks created before the specified cutoff date.
        """
        self.client.force_authenticate(user=self.user)
        now = timezone.now()

        # Create two tasks and adjust their 'created_at' timestamps.
        task_old = Task.objects.create(name="Old Task", owner=self.user)
        task_new = Task.objects.create(name="New Task", owner=self.user)
        # Set 'created_at' such that task_old is older than task_new.
        Task.objects.filter(pk=task_old.pk).update(created_at=now - timedelta(days=2))
        Task.objects.filter(pk=task_new.pk).update(created_at=now - timedelta(days=1))

        # Define the cutoff date: tasks created before this date should be returned.
        cutoff = now - timedelta(days=1)
        url_with_before = f"{self.list_url}?created_at_before={cutoff.date()}"
        response = self.client.get(url_with_before)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get("results", [])
        returned_ids = [t["id"] for t in results]

        # Verify that only the older task is included.
        self.assertIn(str(task_old.id), returned_ids)
        self.assertNotIn(str(task_new.id), returned_ids)
