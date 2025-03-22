# Django imports
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError

# Internal imports
from Task.models import Task

User = get_user_model()


class TaskModelTest(TestCase):
    def setUp(self):
        # User objects related set up
        self.user = User.objects.create_user(username='user1', password='<PASSWORD>', email='<EMAIL>')
        self.other_user = User.objects.create_user(username='user2', password='<PASSWORD>', email='<EMAIL>')

    def test_unique_task_name_per_owner(self):
        """
        Verify that a user cannot create two tasks with the same name.
        Uniqueness is enforced at the database level; therefore, full_clean()
        might not catch the error, so we check for an IntegrityError on saving.
        """
        Task.objects.create(owner=self.user, name='Test', description='Description 1')
        duplicate_task = Task(owner=self.user, name='Test', description='Description 2')

        with self.assertRaises(IntegrityError):
            duplicate_task.save()

    def test_unique_task_name_for_different_users(self):
        """
        Verify that tasks with the same name are allowed for different users.
        """
        task1 = Task.objects.create(owner=self.user, name='Test', description='Description 1')
        task2 = Task.objects.create(owner=self.other_user, name='Test', description='Description 2')

        self.assertEqual(task1.name, task2.name)