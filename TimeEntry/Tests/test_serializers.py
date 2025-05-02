# Python Imports
from datetime import datetime, timedelta
# Django Imports
from django.utils.dateparse import parse_datetime
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils.timezone import now
# DRF Imports
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIRequestFactory
# Internal Imports
from TimeMate.Utils.test_helpers import get_error_code
from Task.models import Task
from TimeEntry.models import TimeEntry
from TimeEntry.serializers import TimeEntryCreateSerializer, TimeEntryListSerializer
from TimeEntry.validators import VALIDATION_ERROR_CODE_INVALID_TIME_RANGE

User = get_user_model()


# # TODO [InProgress/NOTE] : This test class is a Work In Progress.
# The existing tests are under active development and are subject to further reviews and refinements.
class TimeEntryCreateSerializerTests(TestCase):
    """
    Tests for TimeEntryCreateSerializer.
    This class verifies the serializer's validation and object creation logic.
    """

    def setUp(self):
        # Set up user and task objects for testing.
        self.user = User.objects.create_user(
            username='testuser', email='<EMAIL>', password='<PASSWORD>'
        )
        self.task = Task.objects.create(name='Test Task', owner=self.user)

        # Simulate an API request context.
        factory = APIRequestFactory()
        self.request = factory.post('/')
        self.request.user = self.user
        self.context = {'request': self.request}

        # Define valid input data for creating a TimeEntry.
        self.valid_data = {
            'task': self.task.id,
            'start_time': datetime.now(),
            'end_time': datetime.now() + timedelta(hours=1)
        }

    def test_valid_time_entry_data(self):
        """
        Verify that valid TimeEntry data is accepted and creates an object.
        """
        serializer = TimeEntryCreateSerializer(data=self.valid_data, context=self.context)
        # Validate serializer data.
        self.assertTrue(serializer.is_valid())
        # Save the object and perform assertions.
        time_entry = serializer.save()
        self.assertIsInstance(time_entry, TimeEntry)
        self.assertEqual(time_entry.owner, self.user)
        self.assertEqual(serializer.validated_data['task'], self.task)

    def test_start_time_equals_end_time(self):
        """
        Verify that validation fails when start_time equals end_time.
        """
        invalid_data = self.valid_data.copy()
        invalid_data['start_time'] = invalid_data['end_time']
        serializer = TimeEntryCreateSerializer(data=invalid_data, context=self.context)
        # Expect a ValidationError due to invalid time range.
        with self.assertRaises(ValidationError) as context_manager:
            serializer.is_valid(raise_exception=True)

        errors = context_manager.exception.detail['non_field_errors']
        self.assertEqual(get_error_code(errors), VALIDATION_ERROR_CODE_INVALID_TIME_RANGE)

    def test_start_time_after_end_time(self):
        """
        Verify that validation fails when start_time is after end_time.
        """
        invalid_data = self.valid_data.copy()
        invalid_data['start_time'] = invalid_data['end_time'] + timedelta(hours=1)
        serializer = TimeEntryCreateSerializer(data=invalid_data, context=self.context)
        # Expect a ValidationError because start_time is later than end_time.
        with self.assertRaises(ValidationError) as context_manager:
            serializer.is_valid(raise_exception=True)

        errors = context_manager.exception.detail['non_field_errors']
        self.assertEqual(get_error_code(errors), VALIDATION_ERROR_CODE_INVALID_TIME_RANGE)

    def test_missing_required_fields(self):
        """
        Verify that validation fails when required fields are missing.
        """
        invalid_data = {}
        serializer = TimeEntryCreateSerializer(data=invalid_data, context=self.context)
        # The serializer should be invalid if required fields are absent.
        self.assertFalse(serializer.is_valid())


# TODO [InProgress/NOTE] : This test class is a Work In Progress.
# The existing tests are under active development and are subject to further reviews and refinements.
class TimeEntryListSerializerTests(TestCase):

    def setUp(self):
        # Set up user and task objects for testing.
        self.user = User.objects.create_user(
            username='testuser', email='<EMAIL>', password='<PASSWORD>'
        )
        self.task = Task.objects.create(name='Test Task', owner=self.user)

        # Simulate an API request context.
        factory = APIRequestFactory()
        self.request = factory.post('/')
        self.request.user = self.user
        self.context = {'request': self.request}

        self.time_entry = TimeEntry.objects.create(
            owner=self.user,
            task=self.task,
            start_time=now(),
            end_time=now() + timedelta(hours=1)
        )

    def test_serialization(self):
        serializer = TimeEntryListSerializer(instance=self.time_entry, context=self.context)
        self.assertEqual(serializer.data['id'], str(self.time_entry.id))
        self.assertEqual(serializer.data['task']['name'], self.task.name)
        expected_start_time = parse_datetime(serializer.data['start_time'])
        expected_end_time = parse_datetime(serializer.data['end_time'])

        self.assertEqual(self.time_entry.start_time, expected_start_time)
        self.assertEqual(self.time_entry.end_time, expected_end_time)
