# Django imports
from django.urls import reverse
from django.contrib.auth import get_user_model
# DRF imports
from rest_framework import status
from rest_framework.test import APITestCase
from Task.validators import VALIDATION_ERROR_CODE_UNIQUE_TASK_NAME

User = get_user_model()


class TaskCreateViewTests(APITestCase):
    def setUp(self):
        # Set up user objects for testing.
        self.user1 = User.objects.create_user(username='user1', password='<PASSWORD>', email='<EMAIL>')
        self.user2 = User.objects.create_user(username='user2', password='<PASSWORD>', email='<EMAIL>')
        # Set up request parameters.
        self.url = reverse('task_create')

    def test_create_task_successful(self):
        """
        Create a task - the owner should be the currently authenticated user.
        """
        self.client.force_authenticate(user=self.user1)
        data = {
            'name': 'Test Task',
            'description': 'Test description',
        }

        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], data['name'])
        self.assertEqual(response.data['description'], data['description'])

    def test_create_task_duplicate_name_with_the_same_user(self):
        """
        Creating two tasks with the same name for the same user should return a 400 error.
        """
        self.client.force_authenticate(user=self.user1)
        data = {
            'name': 'Test Task',
            'description': 'First instance',
        }

        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Try to create a task with the same name for the same user.
        data['description'] = 'Second instance'
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Expect a validation error (non_field_errors) due to duplicate task name.
        self.assertIn('non_field_errors', response.data)
        errors = response.data['non_field_errors']
        error_code = errors[0].code
        self.assertEqual(error_code, VALIDATION_ERROR_CODE_UNIQUE_TASK_NAME)

    def test_owner_field_is_ignored_in_input(self):
        """
        The owner field provided in the input should be ignored and replaced with the current user.
        """
        self.client.force_authenticate(user=self.user1)
        # Try to send a different owner in the input data.
        data = {
            'name': 'Test Task',
            'description': 'Test description',
            'owner': self.user2.pk
        }
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Even though an owner was sent in the input, user1 should be the actual owner.
        self.assertEqual(response.data['owner']['username'], self.user1.username)
