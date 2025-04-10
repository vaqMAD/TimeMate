# Django imports
from django.test import TestCase
from django.contrib.auth import get_user_model
# DRF imports
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIRequestFactory
# Internal imports
from TimeMate.Utils.utils import get_error_code
from Task.models import Task
from Task.serializers import TaskCreateSerializer, TaskDetailSerializer, TaskListSerializer
from Task.validators import VALIDATION_ERROR_CODE_UNIQUE_TASK_NAME

User = get_user_model()


class TaskSerializerTest(TestCase):
    def setUp(self):
        # User objects related set up
        self.user = User.objects.create_user(username='testuser', email='<EMAIL>', password='<PASSWORD>')

        # View is not used in this test, so we have to simulate it
        factory = APIRequestFactory()
        self.request = factory.post('/')
        self.request.user = self.user
        self.context = {'request': self.request}

        # Validated data
        self.valid_data = {
            'name': 'Test Task',
            'description': 'Test description',
        }

    def test_serializer_valid_data(self):
        """
        Serializer should correctly validate and create an instance with valid data
        """

        serializer = TaskCreateSerializer(data=self.valid_data, context=self.context)
        # Check validation
        self.assertTrue(serializer.is_valid())

        # Save object
        task = serializer.save()

        # Rest of assertions
        self.assertIsInstance(task, Task)
        self.assertEqual(task.owner, self.user)
        self.assertEqual(task.name, self.valid_data['name'])
        self.assertEqual(task.description, self.valid_data['description'])

    def test_serializer_duplicate_task_name_for_the_same_owner(self):
        """
        When trying to create a task wit the same name, for the same user, serializer should report an error
        """

        # Create first Task
        Task.objects.create(**self.valid_data, owner=self.user)

        # Prepare duplicated data,
        duplicate_data = {'name': 'Test Task'}

        # Check is validation running correctly
        serializer = TaskCreateSerializer(data=duplicate_data, context=self.context)
        with self.assertRaises(ValidationError) as context:
            serializer.is_valid(raise_exception=True)

        # Check error msg
        errors = context.exception.detail['non_field_errors']
        self.assertEqual(get_error_code(errors), VALIDATION_ERROR_CODE_UNIQUE_TASK_NAME)
        self.assertIn(self.user.username, str(errors))
        self.assertIn(duplicate_data['name'], str(errors))

    def test_check_correct_formatting(self):
        """
        to_representation method should return owner field as a nested object
        """
        task = Task.objects.create(name="Test task", owner=self.user)
        serializer = TaskCreateSerializer(task, context=self.context)
        rep = serializer.data

        self.assertIsInstance(rep.get('owner'), dict)
        self.assertEqual(rep['owner'].get('username'), self.user.username)
        self.assertEqual(rep['owner'].get('email'), self.user.email)


class TaskDetailSerializerTests(TestCase):
    def setUp(self):
        # User objects related set up
        self.user = User.objects.create_user(username='testuser', email='<EMAIL>', password='<PASSWORD>')

        # Data set up
        self.task = Task.objects.create(name='Sample Task', owner=self.user)

    def test_task_detail_serializer_returns_nested_owner(self):
        serializer = TaskDetailSerializer(instance=self.task)
        data = serializer.data

        self.assertEqual(data['owner']['username'], self.user.username)
        self.assertEqual(data['owner']['email'], self.user.email)


class TaskListSerializerTests(TestCase):
    def setUp(self):
        # User objects related set up
        self.user = User.objects.create_user(username='testuser', email='<EMAIL>', password='<PASSWORD>')

        # Request related set up
        self.factory = APIRequestFactory()
        self.request = self.factory.get('/')
        self.request.user = self.user
        self.context = {'request': self.request}

        # Data set up
        self.task = Task.objects.create(name='Sample Task', owner=self.user)

    def test_task_list_serializer_returns_detail_url(self):
        # Provide context to HyperlinkedIdentityField to generate URL
        serializer = TaskListSerializer(instance=self.task, context=self.context)
        data = serializer.data

        self.assertIn('detail_url', data)
        # Check if the URL contains the expected Task ID
        self.assertIn(str(self.task.id), data['detail_url'])
