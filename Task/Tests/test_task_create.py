# Django imports
from django.urls import reverse
from django.contrib.auth import get_user_model
# DRF imports
from rest_framework import status
# Internal imports
from TimeMate.Utils.test_helpers import get_error_code
from Task.validators import VALIDATION_ERROR_CODE_UNIQUE_TASK_NAME
from .base import BaseTaskAPITestCase


User = get_user_model()


class TaskCreateViewTests(BaseTaskAPITestCase):

    def setUp(self):
        self.url = reverse('task_list_create')

    def test_create_task_successful(self):
        """
        Create a task - the owner should be the currently authenticated user.
        """
        self.authenticate(self.user1)
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
        self.authenticate(self.user1)
        payload = {'name': 'Test Task', 'description': 'First instance'}

        r1 = self.client.post(self.url, payload, format='json')
        self.assertEqual(r1.status_code, status.HTTP_201_CREATED)

        payload['description'] = 'Second instance'
        r2 = self.client.post(self.url, payload, format='json')
        self.assertEqual(r2.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertIn('non_field_errors', r2.data)
        self.assertEqual(
            get_error_code(r2.data['non_field_errors']),
            VALIDATION_ERROR_CODE_UNIQUE_TASK_NAME
        )

    def test_owner_field_is_ignored_in_input(self):
        """
        The owner field provided in the input should be ignored and replaced with the current user.
        """
        self.authenticate(self.user1)
        data = {
            'name': 'Test Task',
            'description': 'Test description',
            'owner': self.user2.pk,
        }
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['owner']['username'], self.user1.username)