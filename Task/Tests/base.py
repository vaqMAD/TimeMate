# Django imports
from django.urls import reverse
from django.contrib.auth import get_user_model
# DRF imports
from rest_framework.test import APITestCase
# Internal imports
from Task.models import Task

User = get_user_model()


class BaseTaskAPITestCase(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create_user(
            username='user1', password='pwd1', email='user1@example.com'
        )
        cls.user2 = User.objects.create_user(
            username='user2', password='pwd2', email='user2@example.com'
        )

    def authenticate(self, user):
        self.client.force_authenticate(user=user)


class BaseTaskListViewTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='user', password='pwd', email='user@example.com'
        )
        cls.other_user = User.objects.create_user(
            username='other_user', password='pwd', email='other@example.com'
        )
        cls.no_task_user = User.objects.create_user(
            username='no_task_user', password='pwd', email='no_task@example.com'
        )

    def setUp(self):
        self.list_url = reverse('task_list_create')

    def authenticate_user(self, user):
        self.client.force_authenticate(user=user)

    @staticmethod
    def create_task(user, amount=1):
        tasks = []
        for i in range(amount):
            task = Task.objects.create(name=f"Task {i} ({user.username})", owner=user)
            tasks.append(task)
        return tasks